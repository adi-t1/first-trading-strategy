import numpy as np
import pandas as pd

def apply_atr_trailing_stop(data: pd.DataFrame, buy_cross: pd.Series, sell_cross: pd.Series, atr_col: str, atr_mult: float, long_only: bool):
    eff_pos = []
    long_trail_series = []
    short_trail_series = []
    stop_event_series = []
    trades = []

    current_pos = 0.0
    long_trail = np.nan
    short_trail = np.nan

    for idx, row in data.iterrows():
        price = row["Close"]
        this_atr = row[atr_col]
        bc = bool(buy_cross.loc[idx]) if not pd.isna(buy_cross.loc[idx]) else False
        sc = bool(sell_cross.loc[idx]) if not pd.isna(sell_cross.loc[idx]) else False

        stopped_today = False
        stop_reason = None
        stop_price = np.nan

        if current_pos == 1:
            if not np.isnan(this_atr):
                new_trail = price - atr_mult * this_atr
                long_trail = new_trail if np.isnan(long_trail) else max(long_trail, new_trail)
            if not np.isnan(long_trail) and price <= long_trail:
                current_pos = 0.0
                stopped_today = True
                stop_reason = "long_stop"
                stop_price = float(price)
                long_trail = np.nan
        elif current_pos == -1 and not long_only:
            if not np.isnan(this_atr):
                new_trail_s = price + atr_mult * this_atr
                short_trail = new_trail_s if np.isnan(short_trail) else min(short_trail, new_trail_s)
            if not np.isnan(short_trail) and price >= short_trail:
                current_pos = 0.0
                stopped_today = True
                stop_reason = "short_stop"
                stop_price = float(price)
                short_trail = np.nan

        if long_only:
            if current_pos == 0 and bc:
                current_pos = 1.0
                long_trail = price - (atr_mult * this_atr if not np.isnan(this_atr) else 0)
            elif current_pos == 1 and sc:
                current_pos = 0.0
                long_trail = np.nan
        else:
            if bc and current_pos != 1:
                current_pos = 1.0
                long_trail = price - (atr_mult * this_atr if not np.isnan(this_atr) else 0)
                short_trail = np.nan
            elif sc and current_pos != -1:
                current_pos = -1.0
                short_trail = price + (atr_mult * this_atr if not np.isnan(this_atr) else 0)
                long_trail = np.nan

        prev_pos = eff_pos[-1] if eff_pos else 0.0
        if stopped_today and prev_pos != current_pos:
            trades.append({
                "datetime": idx,
                "action": "SELL" if prev_pos == 1 else ("COVER" if prev_pos == -1 else "FLAT"),
                "reason": stop_reason,
                "price": float(stop_price) if not np.isnan(stop_price) else float(price),
                "from_pos": prev_pos,
                "to_pos": current_pos,
            })

        if prev_pos != current_pos and not stopped_today:
            if current_pos == 1 and prev_pos <= 0:
                trades.append({
                    "datetime": idx,
                    "action": "BUY",
                    "reason": "buy_cross",
                    "price": float(price),
                    "from_pos": prev_pos,
                    "to_pos": current_pos,
                })
            elif current_pos == 0 and prev_pos == 1 and long_only:
                trades.append({
                    "datetime": idx,
                    "action": "SELL",
                    "reason": "sell_cross",
                    "price": float(price),
                    "from_pos": prev_pos,
                    "to_pos": current_pos,
                })
            elif current_pos == -1 and prev_pos >= 0 and not long_only:
                trades.append({
                    "datetime": idx,
                    "action": "SHORT",
                    "reason": "sell_cross",
                    "price": float(price),
                    "from_pos": prev_pos,
                    "to_pos": current_pos,
                })
            elif current_pos == 1 and prev_pos == -1 and not long_only:
                trades.append({
                    "datetime": idx,
                    "action": "COVER+BUY",
                    "reason": "buy_cross",
                    "price": float(price),
                    "from_pos": prev_pos,
                    "to_pos": current_pos,
                })

        eff_pos.append(current_pos)
        long_trail_series.append(long_trail)
        short_trail_series.append(short_trail)
        stop_event_series.append(stopped_today)

    return (
        pd.Series(eff_pos, index=data.index, name="PositionEff"),
        pd.Series(long_trail_series, index=data.index, name="LongTrail"),
        pd.Series(short_trail_series, index=data.index, name="ShortTrail"),
        pd.Series(stop_event_series, index=data.index, name="StopEvent"),
        pd.DataFrame(trades),
    )


