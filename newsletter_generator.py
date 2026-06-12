import html
import pandas as pd

def build_newsletter(data: dict, app_name: str = "앱") -> str:
    df_w1   = data.get("지지난주_SensorTower", pd.DataFrame())
    df_w2   = data.get("지난주_SensorTower",   pd.DataFrame())
    df_buzz = data.get("네이버_버즈뉴스",        pd.DataFrame())

    u1, r1, u2, r2 = 0, 0, 0, 0

    if not df_w1.empty and "u" in df_w1.columns and "r" in df_w1.columns:
        val_u1 = df_w1["u"].iloc[0]
        val_r1 = df_w1["r"].iloc[0]
        u1 = int(str(val_u1)) if pd.notna(val_u1) else 0
        r1 = int(str(val_r1)) if pd.notna(val_r1) else 0

    if not df_w2.empty and "u" in df_w2.columns and "r" in df_w2.columns:
        val_u2 = df_w2["u"].iloc[0]
        val_r2 = df_w2["r"].iloc[0]
        u2 = int(str(val_u2)) if pd.notna(val_u2) else 0
        r2 = int(str(val_r2)) if pd.notna(val_r2) else 0

    u_chg = round((u2 - u1) / u1 * 100, 1) if u1 != 0 else 0
    r_chg = round((r2 - r1) / r1 * 100, 1) if r1 != 0 else 0

    top_news_items = []
    if not df_buzz.empty:
        for _, row in df_buzz.head(3).iterrows():
            title   = html.unescape(str(row.get('뉴스_제목', '')))
            summary = html.unescape(str(row.get('뉴스_요약', '')))
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
