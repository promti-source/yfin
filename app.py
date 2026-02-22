import streamlit as st
import yfinance as yf
import pandas as pd

st.title("📈 リアルタイム株価モニター")

ticker = st.sidebar.text_input("ティッカーシンボルを入力 (例: 7203.T, AAPL)", "7203.T")

# 修正ポイント1: データの取得方法をより確実に
# auto_adjust=True, multi_level_download=False を追加してデータを平坦化します
data = yf.download(ticker, period="1d", interval="1m", auto_adjust=True, multi_level_download=False)

if not data.empty:
    try:
        # 修正ポイント2: 最新の終値を抽出し、強制的に数値(float)に変換
        # data['Close']がSeries（列）なので、最後の1要素を数値として取り出します
        latest_price_raw = data['Close'].iloc[-1]
        
        # 万が一、配列で返ってきた場合でも最初の1つを取る処理
        if isinstance(latest_price_raw, pd.Series):
            latest_price = float(latest_price_raw.iloc[0])
        else:
            latest_price = float(latest_price_raw)

        # 表示
        st.metric(label=f"{ticker} の現在値", value=f"{latest_price:,.2f} JPY")

        st.subheader("本日の値動き (1分足)")
        st.line_chart(data['Close'])
        
    except Exception as e:
        st.error(f"データの解析中にエラーが発生しました: {e}")
else:
    st.error("データが取得できませんでした。シンボルが正しいか、または市場が閉まっていないか確認してください。")