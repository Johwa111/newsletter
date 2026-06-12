import requests
import pandas as pd
from datetime import timedelta, date
import os
import json

SENSOR_TOWER_TOKEN       = os.environ["SENSOR_TOWER_TOKEN"]
SENSOR_TOWER_URL         = "https://api.sensortower.com/v1/android/sales_report_estimates"
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

def get_sensortower_data(app_id, token, start_dt, end_dt):
    params = {"app_ids": app_id, "date_granularity": "weekly",
              "start_date": start_dt.strftime("%Y-%m-%d"),
              "end_date": end_dt.strftime("%Y-%m-%d"), "auth_token": token}
    try:
        response = requests.get(SENSOR_TOWER_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            return pd.DataFrame(data)
        elif isinstance(data, dict) and "data" in data:
            return pd.DataFrame(data["data"])
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ [SensorTower] 오류: {e}")
        return pd.DataFrame()

def get_naver_news_buzz(keyword, client_id, client_secret, display=10):
    headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
    params  = {"query": keyword, "display": display, "sort": "date"}
    try:
        response = requests.get(NAVER_NEWS_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if "items" in data and data["items"]:
            df = pd.DataFrame(data["items"])[["title", "description", "pubDate", "link"]]
            df.columns = ["뉴스_제목", "뉴스_요약", "발행일", "링크"]
            df["뉴스_제목"] = df["뉴스_제목"].str.replace(r"<[^>]+>", "", regex=True)
            df["뉴스_요약"] = df["뉴스_요약"].str.replace(r"<[^>]+>", "", regex=True)
            return df
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ [NaverBuzz] 오류: {e}")
        return pd.DataFrame()

def combine_data(df_w1, df_w2, df_buzz):
    return {"지지난주_SensorTower": df_w1, "지난주_SensorTower": df_w2, "네이버_버즈뉴스": df_buzz}

if __name__ == "__main__":
    from newsletter_generator import build_newsletter
    from slack_sender import send_to_slack

    with open("apps.json", "r", encoding="utf-8") as f:
        apps_config = json.load(f)

    for app_info in apps_config:
        app_name = app_info.get("name", "Unknown App")
        app_id   = app_info.get("sensortower_app_id")
        keyword  = app_info.get("naver_news_keyword")

        print(f"\n--- {app_name} 뉴스레터 생성 시작 ---")
        df_w1   = get_sensortower_data(app_id, SENSOR_TOWER_TOKEN, w1_start, w1_end)
        df_w2   = get_sensortower_data(app_id, SENSOR_TOWER_TOKEN, w2_start, w2_end)
        df_buzz = get_naver_news_buzz(keyword, NAVER_CLIENT_ID, NAVER_CLIENT_SECRET)
        data    = combine_data(df_w1, df_w2, df_buzz)

        newsletter = build_newsletter(data, app_name)
        send_to_slack(newsletter, SHARED_SLACK_WEBHOOK_URL, app_name)
        print(f"--- {app_name} 전송 완료 ---")
