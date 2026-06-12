import requests

def send_to_slack(newsletter: str, webhook_url: str, app_name: str = "앱"):
    r = requests.post(webhook_url, json={"text": newsletter})
    print(f"✅ Slack 전송 완료 ({app_name})" if r.status_code == 200 else f"❌ 실패: {r.text}")
