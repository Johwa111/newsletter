import html

def build_newsletter(data: dict, app_name: str = "앱") -> str:
    df_w1   = data["지지난주_SensorTower"]
    df_w2   = data["지난주_SensorTower"]
    df_buzz = data["네이버_버즈뉴스"]

    u1, r1 = int(df_w1["u"].iloc[0]), int(df_w1["r"].iloc[0])
    u2, r2 = int(df_w2["u"].iloc[0]), int(df_w2["r"].iloc[0])
    u_chg  = round((u2 - u1) / u1 * 100, 1) if u1 != 0 else 0
    r_chg  = round((r2 - r1) / r1 * 100, 1) if r1 != 0 else 0

    top_news_items = []
    if not df_buzz.empty:
        for _, row in df_buzz.head(3).iterrows():
            title   = html.unescape(str(row['뉴스_제목']))
            summary = html.unescape(str(row['뉴스_요약']))
            top_news_items.append(
                f"- {title[:60].strip()}: {summary[:80].strip()}..."
            )
    else:
        top_news_items.append("- 이번 주 주요 뉴스 소식이 없습니다.")

    top_news = "\n".join(top_news_items)

    return f"""
📰 {app_name} 주간 퍼포먼스 뉴스레터

📈 주요 지표 (WoW)
- 다운로드 : {u1:,} → {u2:,} 건 ({u_chg:+}%)
- 매출     : {r1:,} → {r2:,} 원 ({r_chg:+}%)

🗞️ 주요 뉴스 버즈 TOP 3
{top_news}

💡 다음 주 액션 아이템
- 지표 상승/하락 요인 심층 분석
- 긍정 버즈 확산을 위한 추가 PR 검토
"""
