import requests

def send_to_slack(newsletter: str, webhook_url: str, app_name: str = "앱"):
    payload = {"text": f"📰 *{app_name} 주간 뉴스레터*\n\n{newsletter}"}
    r = requests.post(webhook_url, json=payload)
    print("✅ Slack 전송 완료" if r.status_code == 200 else f"❌ 실패: {r.text}")
