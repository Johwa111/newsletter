import openai, os

def build_newsletter(data: dict) -> str:
    df_w1   = data["지지난주_SensorTower"]
    df_w2   = data["지난주_SensorTower"]
    df_buzz = data["네이버_버즈뉴스"]

    # SensorTower WoW 지표 계산
    u1, r1 = int(df_w1["u"].iloc[0]), int(df_w1["r"].iloc[0])
    u2, r2 = int(df_w2["u"].iloc[0]), int(df_w2["r"].iloc[0])
    u_chg = round((u2 - u1) / u1 * 100, 1)
    r_chg = round((r2 - r1) / r1 * 100, 1)

    # 뉴스 상위 5건 요약
    news_text = "\n".join(
        f"- {row['뉴스_제목']}: {row['뉴스_요약'][:60]}..."
        for _, row in df_buzz.head(5).iterrows()
    )

    prompt = f"""
아래 데이터를 바탕으로 '나이트크로우' 퍼포먼스 마케팅 주간 뉴스레터를 작성해줘.
형식: ① 핵심 요약 ② 주요 지표 변화 ③ 뉴스 버즈 인사이트 ④ 다음 주 액션 아이템

[SensorTower 지표]
- 지지난주 다운로드: {u1:,} / 매출: {r1:,}
- 지난주   다운로드: {u2:,} ({u_chg:+}%) / 매출: {r2:,} ({r_chg:+}%)

[네이버 버즈뉴스 TOP 5]
{news_text}
"""
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content