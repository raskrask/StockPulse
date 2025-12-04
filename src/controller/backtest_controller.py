
from data.yf_fetcher import fetch_yf_daily, fetch_yf_weekly, fetch_yf_monthly, fetch_yf_info
from typing import Callable, Iterable, List, Dict, Optional
from data.jpx_fetcher import JPXListingFetcher
from screen.screen_factory import ScreenFactory
from screen.screen_record import  ScreenRecord
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import streamlit as st
import json
from data.io_utils import BASE_DIR, load_json, save_json, exists_file

ProgressCallback = Callable[[float, str], None]  # (0.0〜1.0, メッセージ)

class BacktestController:
    def execute_backtest(self, params: dict, progress_callback: Optional[ProgressCallback] = None) -> list:
        """
        指定されたフィルター条件に基づいて銘柄をバックテストする
        """
        jpx = JPXListingFetcher()
        sheet = jpx.fetch_workbook().sheet_by_index(0)

        nrows = sheet.nrows
        candidates = list(range(nrows))[1:]
        params['stockNumbers'] = params.get('stockNumbers', '').strip()
        #params['stockNumbers'] = ['3088.T'] # テスト用に特定銘柄のみ処理
        #candidates = candidates[1040:1250]  # テスト用に最初の300行だけ処理
        filters = ScreenFactory.build_screens(params)

        if progress_callback:
            start_time = datetime.now()
            progress_callback(0, text=f"Start generate_triggers...{nrows} stocks")

        results = []
        for i, x in enumerate(candidates):
            record = ScreenRecord(sheet.row(x))

            progress = (i + 1) / nrows
            if progress_callback:
                progress_callback(progress, text=f"Processing generate_triggers{record.symbol}... ({i+1}/{nrows})")

            if params['stockNumbers'] and record.symbol not in params['stockNumbers']:
                continue

            trigger = self._generate_triggers(record, filters)
            strategy = self._simulate_trading_strategy(record, trigger)

            if strategy is not None:
                results.append({
                    "symbol": record.symbol,
                    "name": record.name,
                    "values": record.get_values(),
                    "buy_signal": trigger,
                    "sell_signal": strategy,
                })
                #st.write(f"{record.symbol} trigger: {trigger}, strategy: {results[-1]}")

    
        if progress_callback:
            progress_callback(1.0, text=f"Completed in {datetime.now() - start_time}")

        metrics = self._compute_backtest_metrics(results, params=params)
        return metrics

    def _compute_backtest_metrics(self, strategy: list, params: dict) -> dict:
        """
        バックテストの結果から評価指標（勝率、PF、最大ドローダウンなど）を計算する
        """
        
        # 勝率
        win_rate = sum(x["sell_signal"]["result"] == "win" for x in strategy) / len(strategy)
        lose_rate = sum(x["sell_signal"]["result"] == "lose" for x in strategy) / len(strategy)
        draw_rate = sum(x["sell_signal"]["result"] == "draw" for x in strategy) / len(strategy)
        # Profit Factor
        returns = [(x["sell_signal"]["close"]-x["buy_signal"]["close"])/x["buy_signal"]["close"] for x in strategy]
        #returns = [(x["sell_signal"]["close"]-x["buy_signal"]["close"])*100 for x in strategy]
        #returns = [(x["sell_signal"]["close"]-x["buy_signal"]["close"]) for x in strategy]
        trade_term = [x["sell_signal"]["date"]-x["buy_signal"]["date"] for x in strategy]
        gross_profit = sum([x for x in returns if x > 0])
        gross_loss = -sum([x for x in returns if x < 0])
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else np.inf
        total_return = gross_profit - gross_loss

        # 最大ドローダウン
        total_return = sum([x for x in returns])
#        roll_max = total_return.cummax()
#        dd = (total_return - roll_max) / roll_max
#        max_drawdown = dd.min()

        return {
            "trades": len(strategy),
            "win_rate": win_rate,
            "lose_rate": lose_rate,
            "draw_rate": draw_rate,
            "gross_profit": gross_profit,
            "gross_loss": gross_loss,
            "profit_factor": profit_factor,
            "trade_term_avg": np.mean([t.days for t in trade_term]),
#            "max_drawdown": max_drawdown,
            "total_return": total_return,
            "strategy": strategy,
        }
        pass

    def _simulate_trading_strategy(self, record, trigger) -> list:
        """
        トリガーに基づいて仮想取引をシミュレーションする
        """
        if trigger is None or len(trigger) == 0:
            return None

        filename = f"{BASE_DIR}/{record.symbol}/backtest/strategy.json"
        if exists_file(filename):
            return load_json(filename)

        df = record.recent_yf_yearly()

        # 購入以降の期間を切り出す
        buy_window = df[df["date"] >= trigger["date"]].copy()
        buy_prices = buy_window['close'][:90]  # 購入後90日間を対象

        # 利益・損失の閾値
        strategy_profit = buy_prices.iloc[0] * 1.07
        strategy_loss   = buy_prices.iloc[0] * 0.95

        # 利益・損失達成インデックス
        profit_idx = buy_prices[buy_prices >= strategy_profit].index
        loss_idx   = buy_prices[buy_prices <= strategy_loss].index

        # 判定
        strategy = None
        if len(profit_idx) == 0 and len(loss_idx) == 0:
            #return None
            strategy = {'result': 'draw', **df.loc[90].to_dict()}  # 90日間で決着がつかなかった場合は引き分けとする

        elif len(profit_idx) == 0:
            strategy = {'result': 'lose', **df.loc[loss_idx[0]].to_dict()}
        elif len(loss_idx) == 0:
            strategy = {'result': 'win', **df.loc[profit_idx[0]].to_dict()}
        else:
            # 先に到達した方で勝敗を決定
            if profit_idx[0] < loss_idx[0]:
                strategy = {'result': 'win', **df.loc[profit_idx[0]].to_dict()}
            else:
                strategy = {'result': 'lose', **df.loc[loss_idx[0]].to_dict()}

        save_json(strategy, filename)
        return strategy

    def _generate_triggers(self, record, filters) -> list:
        """
        フィルター条件に基づいて、売買トリガー（シグナル）を生成する
        """
        filename = f"{BASE_DIR}/{record.symbol}/backtest/triggers.json"
        if exists_file(filename):
            return load_json(filename)

        df = record.recent_yf_yearly()
        days = len(df)    
        flags = [True] * days        
        for f in filters:
            current = f.batch_apply(record, days)
            df = df.copy()
            df[f.key] = current
            flags = [a and b for a, b in zip(flags, current)]
            if not any(flags):
                break

        if any(flags):
            first_trigger = next((i for i, x in enumerate(flags) if x), None)
            trigger = df.iloc[first_trigger].to_dict()
            save_json(trigger, filename)

            return trigger

        save_json({}, filename)
        return None
