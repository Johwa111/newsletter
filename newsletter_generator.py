import html, pandas as pd

def get_metrics(data):
    df1 = data.get("지지난주_SensorTower", pd.DataFrame())
    df2 = data.get("지난주_SensorTower",   pd.DataFrame())
    def v(df, col):
        if df.empty or col not in df.columns: return 0
        x = df[col].iloc[0]; return int(str(x)) if pd.notna(x) else 0
    u1,r1,u2,r2 = v(df1,"u"),v(df1,"r"),v(df2,"u"),v(df2,"r")
    return u1,r1,u2,r2, round((u2-u1)/u1*100,1) if u1 else 0, round((r2-r1)/r1*100,1) if r1 else 0

def build_newsletter(app_name, w1s, w1e, w2s, w2e, data_total, data_aos, data_ios, df_buzz):
    u1a,r1a,u2a,r2a,uc_a,rc_a = get_metrics(data_aos)
    u1i,r1i,u2i,r2i,uc_i,rc_i = get_metrics(data_ios)

    news = []
    if not df_buzz.empty:
        for _,row in df_buzz.head(5).iterrows():
            t = html.unescape(str(row.get("뉴스_제목","")))
            l = str(row.get("링크",""))
            news.append(f"- <{l}|{t[:80].strip()}>")
    else:
        news.append("- 이번 주 주요 뉴스 소식이 없습니다.")

    body  = f"📰 *{app_name} 주간 퍼포먼스 뉴스레터*\n"
    body += f"📅 *확인 주차*: {w1s} 주차 → {w2s} 주차\n\n"

    if u1a or r1a or u2a or r2a:
        body += f"🤖 *AOS 주요 지표 (WoW)*\n"
        body += f"- 다운로드 : {u1a:,} → {u2a:,} 건 ({uc_a:+}%)\n"
        body += f"- 매출     : {r1a:,} → {r2a:,} 원 ({rc_a:+}%)\n\n"

    if u1i or r1i or u2i or r2i:
        body += f"🍎 *iOS 주요 지표 (WoW)*\n"
        body += f"- 다운로드 : {u1i:,} → {u2i:,} 건 ({uc_i:+}%)\n"
        body += f"- 매출     : {r1i:,} → {r2i:,} 원 ({rc_i:+}%)\n\n"

    body += f"🗞️ *주요 뉴스 버즈 TOP 5*\n{chr(10).join(news)}\n"
    body += "\n\n――――――――――――――――――――\n\n\n"
    return body
