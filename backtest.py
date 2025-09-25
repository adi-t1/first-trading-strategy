import numpy as np
import pandas as pd

def compute_returns(data: pd.DataFrame, position_col: str, cost_bps: float) -> pd.DataFrame:
    out = data.copy()
    out["Return"] = out["Close"].pct_change()
    out["StrategyReturn"] = out[position_col].shift(1) * out["Return"]
    cost_rate = float(cost_bps) / 10000.0
    trades = out[position_col].diff().abs().fillna(0)
    out["StrategyReturn"] = out["StrategyReturn"] - (trades * cost_rate)
    out["Equity"] = (1 + out["StrategyReturn"].fillna(0)).cumprod()
    return out

def metrics(equity: pd.Series, strategy_return: pd.Series) -> dict:
    r = strategy_return.dropna()
    if len(r) == 0 or equity.empty:
        return {"CAGR": np.nan, "Sharpe": np.nan, "MaxDrawdown": np.nan}
    periods_per_year = 252
    total_return = float(equity.iloc[-1])
    num_periods = int(len(r))
    cagr = total_return ** (periods_per_year / max(1, num_periods)) - 1
    vol = float(r.std())
    mean_ret = float(r.mean())
    sharpe = (mean_ret * np.sqrt(periods_per_year)) / vol if (not np.isnan(vol) and vol > 0) else np.nan
    cummax = equity.cummax()
    drawdown = equity / cummax - 1
    max_dd = float(drawdown.min())
    return {"CAGR": cagr, "Sharpe": sharpe, "MaxDrawdown": max_dd}


