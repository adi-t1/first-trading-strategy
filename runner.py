import numpy as np
import pandas as pd

from data import download_ohlc
from indicators import moving_averages, average_true_range
from signals import crossover_signals
from stops import apply_atr_trailing_stop
from backtest import compute_returns, metrics
from plotting import plot_price_and_signals, plot_combined_equity

def run_symbol(
    symbol: str,
    short: int = 20,
    long: int = 50,
    period: str = "1y",
    use_ema: bool = False,
    long_only: bool = True,
    cost_bps: float = 10,
    use_trailing_stop: bool = True,
    atr_window: int = 14,
    atr_mult: float = 3.0,
    plot: bool = True,
    verbose: bool = True,
):
    data = download_ohlc(symbol, period)
    ma = moving_averages(data["Close"], short, long, use_ema)
    data = pd.concat([data, ma], axis=1)
    signal, buy_cross, sell_cross = crossover_signals(data["ShortMA"], data["LongMA"])
    data["Signal"] = signal

    if use_trailing_stop:
        data["ATR"] = average_true_range(data.get("High", data["Close"]), data.get("Low", data["Close"]), data["Close"], atr_window)
        pos_eff, long_trail, short_trail, stop_event, trades = apply_atr_trailing_stop(
            data, buy_cross, sell_cross, "ATR", atr_mult, long_only
        )
        data = pd.concat([data, pos_eff, long_trail, short_trail, stop_event], axis=1)
    else:
        data["PositionEff"] = np.where(signal > 0, 1.0, (0.0 if long_only else -1.0))
        trades = pd.DataFrame()

    data = compute_returns(data, "PositionEff", cost_bps)
    m = metrics(data["Equity"], data["StrategyReturn"])

    if verbose:
        print(f"Price            Close     ShortMA      LongMA  Signal  Position    Equity")
        tail_df = data[["Close", "ShortMA", "LongMA", "Signal", "PositionEff", "Equity"]].tail()
        # Rename PositionEff to Position for display consistency
        tail_df = tail_df.rename(columns={"PositionEff": "Position"})
        print("Date")
        print(tail_df)
        print(f"CAGR: {m['CAGR']:.2%} | Sharpe: {m['Sharpe']:.2f} | Max Drawdown: {m['MaxDrawdown']:.2%}")
        trade_count = 0 if trades is None or trades.empty else len(trades)
        print(f"Trades executed: {trade_count}")
        if trade_count > 0:
            print(trades.head(min(10, trade_count)))

    if plot:
        plot_price_and_signals(data, short, long, use_ema, buy_cross, sell_cross, use_trailing_stop, long_only, trades)

    return {"data": data, "metrics": m, "trades": trades}

def run_on_symbols(
    symbols=None,
    short=20,
    long=50,
    period="5y",
    use_ema=True,
    long_only=True,
    cost_bps=5,
    use_trailing_stop=True,
    atr_window=14,
    atr_mult=3.0,
    plot_each=False,
    plot_combined=True,
    verbose=True,
):
    if symbols is None:
        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "JPM", "JNJ", "PG"]

    results = {}
    summary_rows = []
    for sym in symbols:
        if verbose:
            print(f"\n=== {sym} ===")
        try:
            res = run_symbol(
                sym, short, long, period, use_ema, long_only, cost_bps,
                use_trailing_stop, atr_window, atr_mult, plot_each, verbose
            )
            results[sym] = res
            mm = res["metrics"]
            trades = res.get("trades") if isinstance(res, dict) else None
            trade_count = int(len(trades)) if trades is not None and not trades.empty else 0
            summary_rows.append({
                "Symbol": sym,
                "CAGR": mm["CAGR"],
                "Sharpe": mm["Sharpe"],
                "MaxDrawdown": mm["MaxDrawdown"],
                "FinalEquity": res["data"]["Equity"].iloc[-1] if "Equity" in res["data"] else np.nan,
                "Trades": trade_count,
            })
        except Exception as exc:
            print(f"Failed for {sym}: {exc}")

    if summary_rows:
        summary = pd.DataFrame(summary_rows).set_index("Symbol").sort_values(by="CAGR", ascending=False)
        if verbose:
            print("\nSummary (sorted by CAGR):")
            print(summary)
    else:
        summary = pd.DataFrame(columns=["CAGR", "Sharpe", "MaxDrawdown", "FinalEquity"])            

    if plot_combined and results:
        plot_combined_equity(results)

    return {"results": results, "summary": summary}


