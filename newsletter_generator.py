import html, pandas as pd

def build_newsletter(data, app_name="앱", w1s="", w1e="", w2s="", w2e=""):
    df_w1   = data.get("지지난주_SensorTower", pd.DataFrame())
    df_w2   = data.get("지난주_SensorTower",   pd.DataFrame())
    df_buzz = data.get("네이버_버즈뉴스",        pd.DataFrame())
    u1=r1=u2=r2=0
    if not df_w1.empty and "u" in df_w1.columns:
        u1 = int(str(df_w1["u"].iloc[0])) if pd.notna(df_w1["u"].iloc[0]) else 0
        r1 = int(str(df_w1["r"].iloc[0])) if pd.notna(df_w1["r"].iloc[0]) else 0
    if not df_w2.empty and "u" in df_w2.columns:
        u2 = int(str(df_w2["u"].iloc[0])) if pd.notna(df_w2["u"].iloc[0]) else 0
        r2 = int(str(df_w2["r"].iloc[0])) if pd.notna(df_w2["r"].iloc[0]) else 0
    u_chg = round((u2-u1)/u1*100,1) if u1 else 0
    r_chg = round((r2-r1)/r1*100,1) if r1 else 0

    news = []
    if not df_buzz.empty:
        for _, row in df_buzz.head(3).iterrows():
            t = html.unescape(str(row.get("뉴스_제목","")))
            l = str(row.get("링크",""))
            news.append(f"- <{l}|{t[:80].strip()}>")
    else:
        news.append("- 이번 주 주요 뉴스 소식이 없습니다.")

    if u_chg > 10 or r_chg > 10:
        action = "- 지표 성장 요인 분석 및 광고 확장 전략 검토\n- 긍정 버즈 연계 콘텐츠 강화"
    elif u_chg < -10 or r_chg < -10:
        action = "- 지표 하락 원인 분석 및 즉각 개선 방안 수립\n- 경쟁사 동향 점검 및 대응 전략 마련"
    else:
        action = "- 현 수준 유지 전략 및 시장 동향 모니터링\n- 신규 유저 유입 채널 다각화 검토"

    return f"""📰 *{app_name} 주간 퍼포먼스 뉴스레터*

📅 {w1s}주차 vs {w2s}주차

📈 *주요 지표 (WoW)*
- 다운로드 : {u1:,} 건 ({w1s}~{w1e}) → {u2:,} 건 ({w2s}~{w2e}) ({u_chg:+}%)
- 매출     : {r1:,} 원 ({w1s}~{w1e}) → {r2:,} 원 ({w2s}~{w2e}) ({r_chg:+}%)

🗞️ *주요 뉴스 버즈 TOP 3*
{chr(10).join(news)}

💡 *다음 주 액션 아이템*
{action}
"""
