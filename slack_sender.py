import requests, os

def send_to_slack(newsletter: str):
    webhook = os.environ["SLACK_WEBHOOK_URL"]
    payload = {"text": f"📰 *나이트크로우 주간 뉴스레터*\n\n{newsletter}"}
    r = requests.post(webhook, json=payload)
    print("✅ Slack 전송 완료" if r.status_code == 200 else f"❌ 실패: {r.text}")