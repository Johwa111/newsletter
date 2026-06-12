import requests
import pandas as pd
from datetime import timedelta, date

# ============================================================
# 1. API 키 설정
# ============================================================
SENSOR_TOWER_APP_ID = "com.wemade.nightcrows"
SENSOR_TOWER_TOKEN  = "ST0_zRyCjD3Y_dIbyj9CosBPXis"
SENSOR_TOWER_URL    = "https://api.sensortower.com/v1/android/sales_report_estimates"

NAVER_CLIENT_ID     = "aelB2xpk5se2WYTF6rR8"
NAVER_CLIENT_SECRET = "JpWNI5TJWx"
NAVER_NEWS_URL      = "https://openapi.naver.com/v1/search/news.json"


# ============================================================
# 2. 날짜 자동 계산
# ============================================================
today    = date.today()
last_sun = today - timedelta(days=today.weekday() + 1)

w1_start = last_sun - timedelta(days=13)
w1_end   = last_sun - timedelta(days=7)
w2_start = last_sun - timedelta(days=6)
w2_end   = last_sun

print(f"📅 지지난주: {w1_start} ~ {w1_end}")
print(f"📅 지난주  : {w2_start} ~ {w2_end}")


# ============================================================
# 3. 센서타워 데이터 수집
# ============================================================
def get_sensortower_data(app_id, token, start_dt, end_dt):
    params = {
        "app_ids"          : app_id,
        "date_granularity" : "weekly",
        "start_date"       : start_dt.strftime("%Y-%m-%d"),
        "end_date"         : end_dt.strftime("%Y-%m-%d"),
        "auth_token"       : token,
    }
    label = f"{start_dt.strftime('%m/%d')}~{end_dt.strftime('%m/%d')}"
    print(f"\n🔍 [SensorTower] 수집 시작 ({label})...")

    try:
        response = requests.get(SENSOR_TOWER_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list) and len(data) > 0:
            df = pd.DataFrame(data)
            print(f"✅ [SensorTower] {len(df)}건 수집 완료.")
            return df
        elif isinstance(data, dict) and "data" in data:
            df = pd.DataFrame(data["data"])
            print(f"✅ [SensorTower] {len(df)}건 수집 완료.")
            return df
        else:
            print(f"⚠️ [SensorTower] 예상과 다른 응답 형식: {data}")
            return pd.DataFrame()

    except requests.exceptions.HTTPError:
        print(f"❌ [SensorTower] HTTP 오류: {response.status_code}")
    except Exception as e:
        print(f"❌ [SensorTower] 예외 발생: {e}")
    return pd.DataFrame()


# ============================================================
# 4. 네이버 버즈(뉴스) 데이터 수집
# ============================================================
def get_naver_news_buzz(keyword, client_id, client_secret, display=10):
    headers = {
        "X-Naver-Client-Id"    : client_id,
        "X-Naver-Client-Secret": client_secret,
    }
    params = {
        "query"  : keyword,
        "display": display,
        "sort"   : "date",
    }
    print(f"\n🔍 [NaverBuzz] 수집 시작 (키워드: '{keyword}')...")

    try:
        response = requests.get(NAVER_NEWS_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if "items" in data and data["items"]:
            df = pd.DataFrame(data["items"])[["title", "description", "pubDate", "link"]]
            df.columns = ["뉴스_제목", "뉴스_요약", "발행일", "링크"]
            df["뉴스_제목"] = df["뉴스_제목"].str.replace(r"<[^>]+>", "", regex=True)
            df["뉴스_요약"] = df["뉴스_요약"].str.replace(r"<[^>]+>", "", regex=True)
            print(f"✅ [NaverBuzz] {len(df)}건 수집 완료.")
            return df
        else:
            print(f"⚠️ [NaverBuzz] 수집된 뉴스가 없습니다.")
            return pd.DataFrame()

    except requests.exceptions.HTTPError:
        print(f"❌ [NaverBuzz] HTTP 오류: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ [NaverBuzz] 예외 발생: {e}")
    return pd.DataFrame()


# ============================================================
# 5. 데이터 통합 (저장 없이 값만 반환) ← 핵심 변경
# ============================================================
def combine_data(df_w1, df_w2, df_buzz):
    result = {
        "지지난주_SensorTower": df_w1,
        "지난주_SensorTower"  : df_w2,
        "네이버_버즈뉴스"       : df_buzz,
    }

    for key, df in result.items():
        if not df.empty:
            print(f"\n📊 [{key}] ({len(df)}행)")
            print(df.to_string(index=False))
        else:
            print(f"\n⚠️ [{key}] 데이터 없음")

    return result  # DataFrame 딕셔너리 반환


# ============================================================
# 6. 실행
# ============================================================
if __name__ == "__main__":
    import json, os
    from newsletter_generator import build_newsletter
    from slack_sender import send_to_slack

    SENSOR_TOWER_TOKEN  = os.environ["SENSOR_TOWER_TOKEN"]
    NAVER_CLIENT_ID     = os.environ["NAVER_CLIENT_ID"]
    NAVER_CLIENT_SECRET = os.environ["NAVER_CLIENT_SECRET"]

    with open("apps.json", "r", encoding="utf-8") as f:
        apps_config = json.load(f)

    for app in apps_config:
        print(f"\n--- {app['name']} 뉴스레터 생성 시작 ---")
        df_w1   = get_sensortower_data(app["sensortower_app_id"], SENSOR_TOWER_TOKEN, w1_start, w1_end)
        df_w2   = get_sensortower_data(app["sensortower_app_id"], SENSOR_TOWER_TOKEN, w2_start, w2_end)
        df_buzz = get_naver_news_buzz(app["naver_news_keyword"], NAVER_CLIENT_ID, NAVER_CLIENT_SECRET)
        data    = combine_data(df_w1, df_w2, df_buzz)
        newsletter = build_newsletter(data, app["name"])
        send_to_slack(newsletter, app["slack_webhook_url"], app["name"])
