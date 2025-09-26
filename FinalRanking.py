import pandas as pd
import json

csv_path = './static/sorted_result.csv'  
data = pd.read_csv(csv_path)

with open('static/selected_tasks.json', 'r', encoding='utf-8') as f:
    selected_tasks = json.load(f)


result2 = data.groupby('User').agg(
    **{task: ('Score', lambda x, task=task: x[data['Task Name'] == task].sum() if task in data['Task Name'].values else 0) for task in selected_tasks},
    LastAnswerTime=('Answer Time', lambda x: x[data['Task Name'].isin(selected_tasks)].max()),  # 根據選定題目計算最大 Answer Time
    TotalScore=('Score', lambda x: sum(x[data['Task Name'] == task].sum() if task in data['Task Name'].values else 0 for task in selected_tasks)),  # 計算選擇題目的分數總和
    Score20Count=('Score', lambda x: (x[data['Task Name'].isin(selected_tasks)] == 20).sum())  # 計算選定題目中分數為 20 的題目數量
).reset_index()

# 檢查是否有 20 分的題目，如果沒有，將Answer Time設為 0
def check_for_20_and_update_time(user_data): 
    # 篩選出Score為 20 的題目
    valid_data = user_data[user_data['Score'] == 20]
    
    if valid_data.empty:
        # 如果沒有得到 20 分的題目，Answer Time設為 0
        return pd.Timedelta(0)
    else:
        # 否則，取Answer Time最晚的紀錄
        return valid_data['Answer Time'].max()

# 使用 apply 來處理每位User的最晚繳交時間
result2['LastAnswerTime'] = result2['User'].apply(
    lambda user: check_for_20_and_update_time(data[(data['User'] == user) & (data['Task Name'].isin(selected_tasks))])
)

#改欄位順序
#cols = ['User', 'TotalScore', 'Quiz1Q1', 'Quiz1Q2', 'Quiz1Q3', 'Quiz1Q4', 'Quiz1Q5', 'Quiz1Q6', 'LastAnswerTime']
#result = result[cols]


# 排名：依照TotalScore、20分題數排序
def count_20_score_tasks(user_data):
    return (user_data['Score'] == 20).sum()


#根據多個條件進行排序
result_sorted = result2.sort_values(
    by=['TotalScore', 'Score20Count', 'LastAnswerTime'],
    ascending=[False, False, True]  # TotalScore降序、Score20Count降序、LastAnswerTime升序
)


# 儲存排序後的結果
result_sorted.to_csv('./static/final.csv', index=False)

print("/static/final.csv已生成")
