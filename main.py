import requests, pandas as pd, os, json
from datetime import timedelta, date

SENSOR_TOWER_TOKEN       = os.environ["SENSOR_TOWER_TOKEN"]
NAVER_CLIENT_ID          = os.environ["NAVER_CLIENT_ID"]
NAVER_CLIENT_SECRET      = os.environ["NAVER_CLIENT_SECRET"]
NAVER_NEWS_URL           = "https://openapi.naver.com/v1/search/news.json"
SHARED_SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]

today    = date.today()
last_sun = today - timedelta(days=today.weekday() + 1)
w1_start = last_sun - timedelta(days=13)
w1_end   = last_sun - timedelta(days=7)
w2_start = last_sun - timedelta(days=6)
w2_end   = last_sun

def get_sensortower_data(app_id, platform, token, start_dt, end_dt):
    if not app_id: return pd.DataFrame()
    url = f"https://api.sensortower.com/v1/{platform}/sales_report_estimates"
    params = {"app_ids": app_id, "date_granularity": "weekly",
              "start_date": start_dt.strftime("%Y-%m-%d"),
              "end_date": end_dt.strftime("%Y-%m-%d"), "auth_token": token}
    try:
        r = requests.get(url, params=params); r.raise_for_status()
        d = r.json()
        if isinstance(d, list) and d: return pd.DataFrame(d)
        if isinstance(d, dict) and "data" in d: return pd.DataFrame(d["data"])
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ [{platform}] {e}"); return pd.DataFrame()

def safe_val(df, col):
    if df.empty or col not in df.columns: return 0
    v = df[col].iloc[0]
    return int(str(v)) if pd.notna(v) else 0

def get_naver_news_buzz(keyword, client_id, client_secret, display=10):
    headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
    params  = {"query": keyword, "display": display, "sort": "date"}
    try:
        r = requests.get(NAVER_NEWS_URL, headers=headers, params=params); r.raise_for_status()
        d = r.json()
        if "items" in d and d["items"]:
            df = pd.DataFrame(d["items"])[["title","description","pubDate","link"]]
            df.columns = ["뉴스_제목","뉴스_요약","발행일","링크"]
            df["뉴스_제목"] = df["뉴스_제목"].str.replace(r"<[^>]+>","",regex=True)
            df["뉴스_요약"] = df["뉴스_요약"].str.replace(r"<[^>]+>","",regex=True)
            return df
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ [NaverBuzz] {e}"); return pd.DataFrame()

if __name__ == "__main__":
    from newsletter_generator import build_newsletter
    from slack_sender import send_to_slack
    with open("apps.json","r",encoding="utf-8") as f:
        apps_config = json.load(f)
    w1s, w1e = w1_start.strftime("%m/%d"), w1_end.strftime("%m/%d")
    w2s, w2e = w2_start.strftime("%m/%d"), w2_end.strftime("%m/%d")

    for app in apps_config:
        name       = app.get("name", "Unknown")
        android_id = app.get("sensortower_android_app_id", "")
        ios_id     = app.get("sensortower_ios_app_id", "")
        keyword    = app.get("naver_news_keyword", "")

        df_w1_aos = get_sensortower_data(android_id, "android", SENSOR_TOWER_TOKEN, w1_start, w1_end)
        df_w2_aos = get_sensortower_data(android_id, "android", SENSOR_TOWER_TOKEN, w2_start, w2_end)
        df_w1_ios = get_sensortower_data(ios_id,     "ios",     SENSOR_TOWER_TOKEN, w1_start, w1_end)
        df_w2_ios = get_sensortower_data(ios_id,     "ios",     SENSOR_TOWER_TOKEN, w2_start, w2_end)

        total_w1 = pd.DataFrame({"u": [safe_val(df_w1_aos,"u") + safe_val(df_w1_ios,"u")],
                                  "r": [safe_val(df_w1_aos,"r") + safe_val(df_w1_ios,"r")]})
        total_w2 = pd.DataFrame({"u": [safe_val(df_w2_aos,"u") + safe_val(df_w2_ios,"u")],
                                  "r": [safe_val(df_w2_aos,"r") + safe_val(df_w2_ios,"r")]})

        df_buzz = get_naver_news_buzz(keyword, NAVER_CLIENT_ID, NAVER_CLIENT_SECRET)

        newsletter = build_newsletter(
            name, w1s, w1e, w2s, w2e,
            {"지지난주_SensorTower": total_w1, "지난주_SensorTower": total_w2},
            {"지지난주_SensorTower": df_w1_aos, "지난주_SensorTower": df_w2_aos},
            {"지지난주_SensorTower": df_w1_ios, "지난주_SensorTower": df_w2_ios},
            df_buzz
        )
        send_to_slack(newsletter, SHARED_SLACK_WEBHOOK_URL, name)
