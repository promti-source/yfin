import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh

# ---------------------------------------------------------
# 1. アプリの基本設定と30秒ごとの自動更新
# ---------------------------------------------------------
st.set_page_config(page_title="株価監視アラート", page_icon="📈")

# 30,000ミリ秒 = 30秒 ごとにページをリロードする
st_autorefresh(interval=30000, key="stock_check_refresh")

st.title("📈 30秒周期・株価監視ツール")
st.caption("Discord通知連携版（回数制限なし・完全無料）")

# ---------------------------------------------------------
# 2. サイドバーの設定（銘柄・目標価格・DiscordのURL）
# ---------------------------------------------------------
st.sidebar.header("通知設定")
ticker = st.sidebar.text_input("銘柄コード (例: 7203.T, NVDA)", "7203.T")
target_price = st.sidebar.number_input("通知する価格 (この価格を超えたら通知)", value=2500.0)
discord_webhook_url = st.sidebar.text_input("Discord Webhook URLを入力", type="password")

# セッション状態で「通知済みフラグ」を管理（同じ価格での連投防止）
if 'last_notified_price' not in st.session_state:
    st.session_state.last_notified_price = 0.0

# ---------------------------------------------------------
# 3. 株価データ取得関数
# ---------------------------------------------------------
def get_stock_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        # 1分足(interval='1m')で最新データを取得
        df = stock.history(period="1d", interval="1m")
        return df
    except Exception as e:
        st.error(f"データ取得エラー: {e}")
        return pd.DataFrame()

df = get_stock_data(ticker)

# ---------------------------------------------------------
# 4. メイン画面の表示と通知の実行
# ---------------------------------------------------------
if not df.empty:
    # 最新の終値を取得
    latest_price = float(df['Close'].iloc[-1])
    
    # 画面に現在値を表示
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="現在の株価", value=f"{latest_price:,.1f} JPY")
    with col2:
        diff = latest_price - target_price
        # 目標価格との差を表示（上がれば赤、下がれば青で表示されます）
        st.metric(label="目標との差額", value=f"{diff:,.1f} JPY", delta=diff)

    # --- 通知の判定ロジック ---
    if latest_price >= target_price:
        st.warning(f"⚠️ 目標価格 {target_price} を突破しました！")
        
        # 前回の通知時と価格が変化している場合のみDiscordに送信（重複防止）
        if latest_price != st.session_state.last_notified_price:
            if discord_webhook_url:
                payload = {
                    "content": f"🚀 **株価アラート**\n【{ticker}】が目標を超えました！\n現在値: **{latest_price:,.1f}** (目標: {target_price})"
                }
                # Discordに送信
                res = requests.post(discord_webhook_url, json=payload)
                
                if res.status_code == 204:
                    st.session_state.last_notified_price = latest_price
                    st.success("Discordへ通知を送信しました。")
                else:
                    st.error("Discord送信に失敗しました。URLが正しいか確認してください。")
            else:
                st.info("サイドバーにURLを入力すると通知が有効になります。")
    else:
        # 価格が目標を下回っている場合は、通知フラグをリセット
        st.session_state.last_notified_price = 0.0

    # グラフの表示
    st.subheader("本日の値動き (1分足チャート)")
    st.line_chart(df['Close'])

else:
    st.info("データがありません。市場が開いている時間帯か、銘柄コードを確認してください。")

# データの末尾を表示（確認用）
with st.expander("生データを確認"):
    st.write(df.tail())