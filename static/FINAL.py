import pandas as pd

# 讀取 CSV 檔案
data = pd.read_csv('aggregated_output.csv')

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

# 輸出為新的 CSV 檔案
result.to_csv('final.csv', index=False)

print("final.csv")

