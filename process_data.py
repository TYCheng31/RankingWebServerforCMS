import psycopg2
import pandas as pd
import csv
from datetime import timedelta

def process_data():
    # 連接資料庫
    conn = psycopg2.connect(
        dbname="cmsdb",
        user="postgres",
        password="0000",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()

    # 存每一筆繳交資料，包含使用者，考試名稱，開始時間，繳交時間，分數，題目名稱
    user_contest_scores = []

    # 查詢 submission_results 資料，根據 submission_id 獲得 score
    cur.execute("SELECT submission_id, score FROM submission_results")
    submission_results = cur.fetchall()

    for submission_result in submission_results:
        submission_id = submission_result[0]  # 提取 submission_id
        score = submission_result[1]         # 提取 score

        # 根據 submission_id 查詢 submissions 資料，獲取 participation_id, task_id, timestamp
        cur.execute("SELECT participation_id, task_id, timestamp FROM submissions WHERE id = %s", (submission_id,))
        submission_data = cur.fetchone()
        if submission_data:
            participation_id = submission_data[0]
            task_id = submission_data[1]
            timestamp = submission_data[2]

            cur.execute("SELECT name FROM tasks WHERE id = %s", (task_id,))
            tasks_data = cur.fetchone()
            if tasks_data:
                task_name = tasks_data[0]

            # 根據 participation_id 查詢 participations 資料，獲取 contest_id 和 user_id
            cur.execute("SELECT contest_id, user_id FROM participations WHERE id = %s", (participation_id,))
            participation_data = cur.fetchone()
            if participation_data:
                contest_id = participation_data[0]
                user_id = participation_data[1]

                # 根據 contest_id 查詢 contests 資料，獲取 contest_name 和 start
                cur.execute("SELECT name, start FROM contests WHERE id = %s", (contest_id,))
                contest_data = cur.fetchone()
                if contest_data:
                    contest_name = contest_data[0]
                    contest_start = contest_data[1]
                else:
                    contest_name = "Unknown"
                    contest_start = "Unknown"

                # 根據 user_id 查詢 users 資料，獲取 first_name
                cur.execute("SELECT first_name FROM users WHERE id = %s", (user_id,))
                user_data = cur.fetchone()
                if user_data:
                    first_name = user_data[0]
                else:
                    first_name = "Unknown"

                # 計算作答時間（繳交時間 - 開始時間）
                if contest_start != "Unknown":
                    contest_start = contest_start.replace(tzinfo=None)  # 去除時區資訊
                    answer_time = timestamp - contest_start
                    answer_time_str = str(answer_time)

                # 準備記錄每次提交的資訊
                user_contest_scores.append({
                    "使用者": first_name,
                    "考試名稱": contest_name,
                    "開始時間": contest_start.strftime("%Y-%m-%d %H:%M:%S") if contest_start != "Unknown" else contest_start,
                    "繳交時間": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "作答時間": answer_time_str,
                    "分數": score,
                    "題目名稱": task_name,
                })

    # 使用 pandas 將結果轉換為 DataFrame
    df = pd.DataFrame(user_contest_scores)

    # 過濾掉分數為 0 的資料
    df_filtered = df[df["分數"] != 0]

    # 先排序資料，先依使用者、考試名稱、題目名稱分組，再按照分數降序排列，若分數相同則按照繳交時間升序排列
    df_sorted = df_filtered.sort_values(by=["使用者", "考試名稱", "題目名稱", "分數", "繳交時間"], ascending=[True, True, True, False, True])

    # 合併相同使用者、考試名稱、題目名稱的資料
    df_grouped = df_sorted.groupby(["使用者", "考試名稱", "題目名稱"], as_index=False).first()

    # 設定 CSV 檔案路徑
    csv_path = "/home/cms/my_flask_app/static/aggregated_output.csv"

    # 開啟 CSV 檔案進行寫入
    df_grouped.to_csv(csv_path, index=False, encoding="utf-8")
    
    print(f"整合後的 CSV 檔案已生成：{csv_path}")

    ###########################################################################################################################
    # 讀取 CSV 檔案
    data = pd.read_csv(csv_path)

    # 處理時間欄位，將 "作答時間" 轉換為 timedelta 格式
    data['作答時間'] = pd.to_timedelta(data['作答時間'])

    # 依據每位使用者進行分組，並計算每一位使用者的各題分數總和
    result = data.groupby('使用者').agg(
        Quiz1Q1分數=('分數', lambda x: x[data['題目名稱'] == 'Quiz1Q1'].sum() if 'Quiz1Q1' in data['題目名稱'].values else 0),
        Quiz1Q2分數=('分數', lambda x: x[data['題目名稱'] == 'Quiz1Q2'].sum() if 'Quiz1Q2' in data['題目名稱'].values else 0),
        Quiz1Q3分數=('分數', lambda x: x[data['題目名稱'] == 'Quiz1Q3'].sum() if 'Quiz1Q3' in data['題目名稱'].values else 0),
        Quiz1Q4分數=('分數', lambda x: x[data['題目名稱'] == 'Quiz1Q4'].sum() if 'Quiz1Q4' in data['題目名稱'].values else 0),
        Quiz1Q5分數=('分數', lambda x: x[data['題目名稱'] == 'Quiz1Q5'].sum() if 'Quiz1Q5' in data['題目名稱'].values else 0),
        Quiz1Q6分數=('分數', lambda x: x[data['題目名稱'] == 'Quiz1Q6'].sum() if 'Quiz1Q6' in data['題目名稱'].values else 0),
        最晚作答時間=('作答時間', 'max')  # 這裡將最晚作答時間更新為作答時間中最晚的紀錄
    ).reset_index()

    # 計算總分
    result['總分'] = result[['Quiz1Q1分數', 'Quiz1Q2分數', 'Quiz1Q3分數', 'Quiz1Q4分數', 'Quiz1Q5分數', 'Quiz1Q6分數']].sum(axis=1)

    # 檢查是否有 20 分的題目，如果沒有，將作答時間設為 0
    def check_for_20_and_update_time(user_data):
        # 篩選出分數為 20 的題目
        valid_data = user_data[user_data['分數'] == 20]
        
        if valid_data.empty:
            # 如果沒有得到 20 分的題目，作答時間設為 0
            return pd.Timedelta(0)
        else:
            # 否則，取作答時間最晚的紀錄
            return valid_data['作答時間'].max()

    # 使用 apply 來處理每位使用者的最晚繳交時間
    result['最晚作答時間'] = result['使用者'].apply(lambda user: check_for_20_and_update_time(data[data['使用者'] == user]))

    # 將 '總分' 欄位移動到 '使用者' 之後
    cols = ['使用者', '總分', 'Quiz1Q1分數', 'Quiz1Q2分數', 'Quiz1Q3分數', 'Quiz1Q4分數', 'Quiz1Q5分數', 'Quiz1Q6分數', '最晚作答時間']
    result = result[cols]

    # 排名：依照總分、20分題數排序
    def count_20_score_tasks(user_data):
        return (user_data['分數'] == 20).sum()

    # 使用 apply 計算得到 20 分的題目數量
    result['得到20分題數'] = result['使用者'].apply(lambda user: count_20_score_tasks(data[data['使用者'] == user]))

    # 根據多個條件進行排序
    result_sorted = result.sort_values(
        by=['總分', '得到20分題數'],
        ascending=[False, False]  # 總分降序、得到 20 分的題數降序
    )

    # 儲存排序後的結果
    result_sorted.to_csv('/home/cms/my_flask_app/static/sorted_result.csv', index=False)

    print("/home/cms/my_flask_app/static/sorted_result.csv 已生成")

    # 關閉資料庫連接
    cur.close()
    conn.close()

# 呼叫處理函式
process_data()
<<<<<<< HEAD

=======
>>>>>>> 77f00d80fa3684f76b819e55cf81c5a9ca097096
