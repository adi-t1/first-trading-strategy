import pandas as pd

def crossover_signals(short_ma: pd.Series, long_ma: pd.Series) -> pd.Series:
    diff = short_ma - long_ma
    prev = diff.shift(1)
    buy = ((diff > 0) & (prev <= 0)).fillna(False)
    sell = ((diff < 0) & (prev >= 0)).fillna(False)
    signal = pd.Series(0, index=short_ma.index)
    signal.loc[buy] = 1
    signal.loc[sell] = -1
    return signal, buy, sell


