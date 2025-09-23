from flask import Flask, render_template, request, redirect, url_for
import os
import csv
import json
import pandas as pd
from datetime import datetime  # 引入 datetime 模組
from process_data import process_data  # 引入你剛定義的函式
import subprocess

app = Flask(__name__)

# 設定靜態檔案的路徑，這樣可以讓 Flask 正確處理靜態檔案
app.config['STATIC_FOLDER'] = '/home/kevin/Desktop/RankingWebServer/static'

@app.route('/', methods=['GET', 'POST'])
def index():
    csv_data = None
    finalcsv_data = None
    task_names = []  # Initialize task_names list
    selected_tasks = []

    # 設定生成的 CSV 路徑
    csv_full_path = os.path.join(app.config['STATIC_FOLDER'], 'sorted_result.csv')
    

    # 讀取 CSV 檔案資料
    if os.path.exists(csv_full_path):
        with open(csv_full_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            csv_data = list(reader)



    # 呼叫處理程式並取得題目名稱
    task_names = process_data()


    # 處理 POST 請求，篩選 CSV 資料
    if request.method == 'POST':
        print("POST request received.")  # 檢查是否進入 POST 請求
        selected_tasks = request.form.getlist('task_names')  # 取得所有勾選的題目名稱
        print(f"Selected tasks: {selected_tasks}")  # 印出選擇的題目名稱

        if selected_tasks:
            # 根據選擇的任務過濾 CSV 資料，假設任務名稱在 CSV 的第三列（索引 2）
            csv_data = [row for row in csv_data if row[2] in selected_tasks]

            # 將選擇的題目名稱保存到 JSON 檔案
            with open(os.path.join(app.config['STATIC_FOLDER'], 'selected_tasks.json'), 'w', encoding='utf-8') as f:
                json.dump(selected_tasks, f)

            print(f"Running command: python3 final.py {csv_full_path}")
            result = subprocess.run(
                ['python3', 'FinalRanking.py'],
                capture_output=True, 
                text=True
            )
            if result.returncode != 0:
                print(f"Error executing final.py: {result.stderr}")
            else:
                print(f"final.py output: {result.stdout}")
    
    # 取得當前時間並格式化為 YYYY-MM-DD HH:MM:SS 格式
    last_updated_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"Final CSV Data: {finalcsv_data}")


    finalcsv_full_path = os.path.join(app.config['STATIC_FOLDER'], 'final.csv')
    if os.path.exists(finalcsv_full_path):
        with open(finalcsv_full_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            finalcsv_data = list(reader)


    return render_template(
        'index.html', 
        csv_data=csv_data, 
        task_names=task_names, 
        selected_tasks=selected_tasks, 
        finalcsv_data=finalcsv_data,
        last_updated_time=last_updated_time
    )

@app.route('/run', methods=['POST'])
def run_script():
    try:
        # 執行資料處理程式並返回結果
        process_data()
        return redirect(url_for('index'))
    except Exception as e:
        return f"執行程式時發生錯誤: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)
