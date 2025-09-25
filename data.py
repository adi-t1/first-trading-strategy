import pandas as pd
import yfinance as yf

def download_ohlc(symbol: str, period: str) -> pd.DataFrame:
    data = yf.download(
        tickers=symbol,
        period=period,
        auto_adjust=False,
        actions=False,
        progress=False,
        threads=True,
        group_by="column",
    )
    if isinstance(data.columns, pd.MultiIndex):
        lvl0 = list(data.columns.get_level_values(0))
        if symbol in lvl0:
            data = data.xs(symbol, axis=1, level=0)
        else:
            lvl1 = list(data.columns.get_level_values(1))
            if symbol in lvl1:
                data = data.xs(symbol, axis=1, level=1)
    data = data.dropna(how="all")
    if not isinstance(data, pd.DataFrame) or data.empty:
        raise RuntimeError("No data downloaded. Check symbol or period.")
    return data


