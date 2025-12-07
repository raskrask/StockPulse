import streamlit as st
import plotly.express as px
import pandas as pd

def backtest_results(results: dict):

    st.title("Backtest Result")

    # --- メトリクスの表示 ---
    col1, col2, col3 = st.columns(3)
    col1.metric("取引回数", results["trades"])
    col2.metric("勝率", f"{results['win_rate']*100:.1f}%")
    col3.metric("敗率", f"{results['lose_rate']*100:.1f}%")

    col4, col5, col6 = st.columns(3)
    col4.metric("プロフィットファクター", f"{results['profit_factor']:.2f}")
    col5.metric("平均保有期間", f"{results['trade_term_avg']:.1f} 日")
    col6.metric("総リターン", f"{results['total_return']:.2f} 倍")

    st.write("---")


    rate_fig = px.pie(
        pd.DataFrame({
        "勝率": ["売確数", "損切り数", "キープ数"],
        "値": [
            results["win_rate"],
            results["lose_rate"],
            results["draw_rate"],
        ]}),
        names="勝率",
        values="値",
        hole=0.3,               # ドーナツ型に
        color="勝率",
        color_discrete_map={
            "売確数": "green",
            "損切り数": "red",
            "キープ数": "gray",
        }
    )
    rate_fig.update_traces(textposition='inside', textinfo='percent+label')

    profit_fig = px.pie(
        pd.DataFrame({
        "収益比率": ["利益率", "損失率"],
        "値": [
            results["gross_profit"],
            results["gross_loss"],
        ]
        }),
        names="収益比率",
        values="値",
        hole=0.3,               # ドーナツ型に
        color="収益比率",
        color_discrete_map={
            "利益率": "green",
            "損失率": "red",
        }
    )
    profit_fig.update_traces(textposition='inside', textinfo='percent+label')


    col21, col22 = st.columns(2)
    col21.plotly_chart(rate_fig, width='stretch')
    col22.plotly_chart(profit_fig, width='stretch')

    st.write("---")
    # buy_signals = [[signal["buy_signal"]["date"],-signal["buy_signal"]["close"]] for signal in results['strategy']]
    # sell_signals = [[signal["sell_signal"]["date"],signal["sell_signal"]["close"]] for signal in results['strategy']]

    # signal_df = pd.DataFrame((sell_signals + buy_signals), columns=["date", "price"])
    # daily_df = signal_df.groupby("date", as_index=False)["price"].sum()
    # daily_df["total"] = daily_df["price"].cumsum()
    # daily_df["total"] = daily_df["total"] * 100

    price = [[s["sell_signal"]["date"], 
              (s["sell_signal"]["close"]-s["buy_signal"]["close"])/s["buy_signal"]["close"]] 
              for s in results['strategy']]
    price_df = pd.DataFrame(price, columns=["date", "price"])
    price_df = price_df.groupby("date", as_index=False)["price"].sum()
    price_df["total"] = price_df["price"].cumsum()


    st.subheader("収益推移グラフ")
    fig = px.line( price_df, x="date", y="total" )    
    st.plotly_chart(fig, width='stretch')


    df = [[s["symbol"],s["name"], s["sell_signal"]["result"],
           s["buy_signal"]["date"], s["buy_signal"]["close"],
           s["sell_signal"]["date"], s["sell_signal"]["close"]] 
           for s in results['strategy']]
    df = pd.DataFrame(df, columns=["symbol", "name", "result", "buy_date", "buy_price", "sell_date", "sell_price"])
    df["return(%)"] = (df["sell_price"] - df["buy_price"]) / df["buy_price"] * 100
    df["return(price)"] = (df["sell_price"] - df["buy_price"]) * 100
    st.write(df)

    # strategy = results['strategy']
    # profit_data = []
    # for s in strategy:
    #     table_data.setdefault("Symbol", []).append(s['symbol'])
    #             symbol = s['symbol']
    #     buy_date = s['buy_signal']['date']
    #     sell_date = s['sell_signal']['date']
    #     buy_price = s['buy_signal']['close']
    #     sell_price = s['sell_signal']['close']
    #     ret = (sell_price - buy_price) / buy_price
    #     profit_data.setdefault("symbol", []).append(symbol)
    #     profit_data.setdefault("buy_date", []).append(buy_date)
    #     profit_data.setdefault("sell_date", []).append(sell_date)
    #     profit_data.setdefault("buy_price", []).append(buy_price)
    #     profit_data.setdefault("sell_price", []).append(sell_price)
    #     profit_data.setdefault("return", []).append(ret)



    # --- 詳細テーブル ---
    st.subheader("Raw Data")
    st.write(results)
    # symbols = " ".join(s['symbol'] for s in backtest_results)
    # st.markdown(f"検索結果({len(backtest_results)})件：`{symbols}`")
    # df = pd.DataFrame(backtest_results).set_index('symbol')
    # st.write(backtest_results)