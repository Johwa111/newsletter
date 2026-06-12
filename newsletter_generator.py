import html
import pandas as pd

def build_newsletter(data: dict, app_name: str = "앱",
                     w1s: str = "", w1e: str = "",
                     w2s: str = "", w2e: str = "") -> str:
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
        for _, row in df_buzz.head(5).iterrows():
            t = html.unescape(str(row.get("뉴스_제목","")))
            l = str(row.get("링크",""))
            news.append(f"- <{l}|{t[:80].strip()}>")
    else:
        news.append("- 이번 주 주요 뉴스 소식이 없습니다.")

    return (
        f"📰 *{app_name} 주간 퍼포먼스 뉴스레터*\n"
        f"📅 *확인 주차*: {w1s} 주차 → {w2s} 주차\n\n"
        f"📈 *주요 지표 (WoW)*\n"
        f"- 다운로드 : {u1:,} 건 ({w1s}~{w1e}) → {u2:,} 건 ({w2s}~{w2e}) ({u_chg:+}%)\n"
        f"- 매출     : {r1:,} 원 ({w1s}~{w1e}) → {r2:,} 원 ({w2s}~{w2e}) ({r_chg:+}%)\n\n"
        f"🗞️ *주요 뉴스 버즈 TOP 5*\n"
        f"{chr(10).join(news)}\n"
        f"\n\n――――――――――――――――――――\n\n\n"
    )
