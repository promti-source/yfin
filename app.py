import streamlit as st
import yfinance as yf
import pandas as pd

# 1. アプリのタイトル
st.title("📈 リアルタイム株価モニター")

# 2. サイドバーで銘柄入力
ticker = st.sidebar.text_input("ティッカーシンボルを入力 (例: 7203.T, AAPL)", "7203.T")

# 3. データの取得
data = yf.download(ticker, period="1d", interval="1m")

if not data.empty:
    # 最新価格の表示
    latest_price = data['Close'].iloc[-1]
    st.metric(label=f"{ticker} の現在値", value=f"{latest_price:.2f} JPY")

    # チャートの表示
    st.subheader("本日の値動き (1分足)")
    st.line_chart(data['Close'])
    
    # データテーブルの表示
    st.write("履歴データ（最新5件）", data.tail())
else:
    st.error("データが見つかりませんでした。シンボルを確認してください。")