import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def plot_price_and_signals(data: pd.DataFrame, short: int, long: int, use_ema: bool, buy_cross: pd.Series, sell_cross: pd.Series, use_trailing_stop: bool, long_only: bool, trade_log: pd.DataFrame | None = None):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, gridspec_kw={"height_ratios": [3, 2]})
    ax1.plot(data.index, data["Close"], label="Close", color="black", linewidth=1)
    ax1.plot(data.index, data["ShortMA"], label=f"{short}-day {'EMA' if use_ema else 'SMA'}")
    ax1.plot(data.index, data["LongMA"], label=f"{long}-day {'EMA' if use_ema else 'SMA'}")
    buy_mask = buy_cross.values if hasattr(buy_cross, "values") else np.array(buy_cross, dtype=bool)
    sell_mask = sell_cross.values if hasattr(sell_cross, "values") else np.array(sell_cross, dtype=bool)
    ax1.plot(data.index[buy_mask], data.loc[buy_mask, "Close"], "^", color="green", markersize=7, label="Buy cross")
    ax1.plot(data.index[sell_mask], data.loc[sell_mask, "Close"], "v", color="red", markersize=7, label="Sell cross")
    if use_trailing_stop:
        ax1.plot(data.index, data.get("LongTrail"), linestyle=":", color="green", alpha=0.6, label="Long trail")
        if not long_only:
            ax1.plot(data.index, data.get("ShortTrail"), linestyle=":", color="red", alpha=0.6, label="Short trail")
        stop_mask = data.get("StopEvent", pd.Series(False, index=data.index)).fillna(False).astype(bool).values
        stop_idx = data.index[stop_mask]
        if len(stop_idx) > 0:
            ax1.plot(stop_idx, data.loc[stop_idx, "Close"], "x", color="orange", markersize=7, label="Stop out")
    # Overlay executed trades if provided
    if trade_log is not None and not trade_log.empty:
        # Ensure datetime index alignment
        tdf = trade_log.copy()
        # Map actions to markers/colors
        style_map = {
            "BUY": ("^", "#2ca02c"),
            "SELL": ("v", "#d62728"),
            "SHORT": ("v", "#9467bd"),
            "COVER": ("x", "#ff7f0e"),
            "COVER+BUY": ("^", "#17becf"),
        }
        for action, (marker, color) in style_map.items():
            mask = tdf["action"] == action
            if mask.any():
                ax1.plot(tdf.loc[mask, "datetime"], tdf.loc[mask, "price"], marker, color=color, markersize=8, linestyle="None", label=f"{action}")
    ax1.legend(loc="upper left")
    ax2.plot(data.index, data["Equity"], label="Equity", color="blue")
    ax2.set_ylabel("Equity (Start=1.0)")
    ax2.legend(loc="upper left")
    plt.tight_layout()
    plt.show()

def plot_combined_equity(results: dict):
    plt.figure(figsize=(12, 6))
    for sym, res in results.items():
        df = res["data"]
        if "Equity" in df:
            plt.plot(df.index, df["Equity"], label=sym)
    plt.title("Combined Equity Curves")
    plt.ylabel("Equity (Start=1.0)")
    plt.legend(loc="upper left", ncol=2)
    plt.tight_layout()
    plt.show()


