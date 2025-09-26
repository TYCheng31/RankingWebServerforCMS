import psycopg2
import pandas as pd
import csv
from datetime import timedelta

# 設定 CSV 檔案路徑
CSV_PATH = "./static/sorted_result.csv"
SORTED_RESULT_PATH = "./static/sorted_result.csv"

def process_data():
    # 連接資料庫
    conn = psycopg2.connect(
        dbname="cmsdb",
        user="cmsuser",
        password="0000",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()

    # 存每一筆繳交資料，包含User，Contest Name，Start Time，Submit Time， Score，Task Name
    user_contest_scores = []
    
    # 存儲所有Task Name的集合
    task_names = set()

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
                # 將Task Name加入集合
                task_names.add(task_name)

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

                # 計算Answer Time（Submit Time - Start Time）
                if contest_start != "Unknown":
                    contest_start = contest_start.replace(tzinfo=None)  # 去除時區資訊
                    answer_time = timestamp - contest_start
                    answer_time_str = str(answer_time)

                # 準備記錄每次提交的資訊
                user_contest_scores.append({
                    "User": first_name,
                    "Contest Name": contest_name,
                    "Start Time": contest_start.strftime("%Y-%m-%d %H:%M:%S") if contest_start != "Unknown" else contest_start,
                    "Submit Time": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "Answer Time": answer_time_str,
                    "Score": score,
                    "Task Name": task_name,
                })

    # 使用 pandas 將結果轉換為 DataFrame
    df = pd.DataFrame(user_contest_scores)

    # 過濾掉 Score為 0 的資料
    df_filtered = df[df["Score"] != 0]

    # 先排序資料，先依User、Contest Name、Task Name分組，再按照 Score降序排列，若 Score相同則按照Submit Time升序排列
    df_sorted = df_filtered.sort_values(by=["User", "Contest Name", "Task Name", "Score", "Submit Time"], ascending=[True, True, True, False, True])

    # 合併相同User、Contest Name、Task Name的資料
    df_grouped = df_sorted.groupby(["User", "Contest Name", "Task Name"], as_index=False).first()

    # 開啟 CSV 檔案進行寫入
    df_grouped.to_csv(CSV_PATH, index=False, encoding="utf-8")
    
    # 將 task_names 進行字母排序
    sorted_task_names = sorted(task_names)

    # 輸出所有Task Name（排序後）
    print("所有Task Name（按字母排序）：", sorted_task_names)
    
    print(f"整合後的 CSV 檔案已生成：{CSV_PATH}")

    return sorted_task_names


# 呼叫處理函式
process_data()
