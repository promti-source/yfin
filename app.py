import streamlit as st
import yfinance as yf
import pandas as pd

st.title("📈 リアルタイム株価モニター")

# サイドバーの設定
ticker_input = st.sidebar.text_input("ティッカーシンボルを入力 (例: 7203.T, AAPL)", "7203.T")

# 1. Tickerオブジェクトを作成（downloadよりこちらが安定します）
stock = yf.Ticker(ticker_input)

# 2. 履歴データの取得 (period="1d", interval="1m" で今日の1分足)
# ※市場が閉まっている時間はデータが空になるため、念のため1dではなく5dにするのも手です
df = stock.history(period="1d", interval="1m")

if not df.empty:
    try:
        # 最新の終値を取得
        # history()で取得したデータは列が「Close」のみのシンプルな構造になります
        latest_price = df['Close'].iloc[-1]
        
        # 前日終値からの変化率（おまけ機能）
        prev_close = df['Close'].iloc[0]
        delta = latest_price - prev_close

        # メトリクスの表示
        st.metric(
            label=f"{ticker_input} の現在値", 
            value=f"{latest_price:,.2f} JPY",
            delta=f"{delta:,.2f}"
        )

        # チャートの表示
        st.subheader("本日の値動き (1分足)")
        st.line_chart(df['Close'])
        
        # データの確認用
        with st.expander("取得した生データを確認"):
            st.write(df.tail())

    except Exception as e:
        st.error(f"表示エラー: {e}")
else:
    st.warning("データが取得できませんでした。以下の原因が考えられます：")
    st.write("1. ティッカーシンボルが間違っている（日本株は末尾に .T が必要）")
    st.write("2. 現在、市場が閉まっていて1分足のデータが存在しない（土日など）")
    st.write("3. Yahoo Financeのサーバー制限")