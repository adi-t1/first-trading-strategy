import pandas as pd

def moving_averages(close: pd.Series, short: int, long: int, use_ema: bool) -> pd.DataFrame:
    if use_ema:
        short_ma = close.ewm(span=short, adjust=False).mean()
        long_ma = close.ewm(span=long, adjust=False).mean()
    else:
        short_ma = close.rolling(short).mean()
        long_ma = close.rolling(long).mean()
    return pd.DataFrame({"ShortMA": short_ma, "LongMA": long_ma})

def average_true_range(high: pd.Series, low: pd.Series, close: pd.Series, window: int) -> pd.Series:
    prev_close = close.shift(1)
    tr = pd.concat([
        (high - low),
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(int(window)).mean()


