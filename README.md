# External Ranking Web Server for CMS

## How to install?

- Get the main file

```bash
git clone https://github.com/TYCheng31/RankingWebServer.git
```

- Use python venv to install all packages

```bash
python3 -m venv RWSVenv
source RWSVenv/bin/activate
pip install flask
pip install psycopg2
pip install pandas
```

- Execute Ranking Web Server

```bash
python3 app.py
```

## Version

### v1.3.0

- 寫死部份改成根據勾選動態改變

### v1.2.0

- 彙整好使用者讀分狀況及總分 (FINAL.py)
- 目前還是寫死

### v1.1.0

- 25/09/19
- 新增設定刷新資料時間

### v1.0.0

- 25/09/16
- 更新仿CMS介面
- 下載勾選指定題目CSV

### v0.0.0

- 25/09/15
- 新增勾選指定題目功能
- 全新前端介面
