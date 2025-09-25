# Trading Strategy – MA Crossover + ATR Trailing Stop

## Overview
Modular Python strategy for equities that downloads OHLC data (`yfinance`), computes SMA/EMA and ATR, generates true moving-average crossovers, applies a volatility-adjusted ATR trailing stop, backtests with transaction costs, logs trades, and plots both price with events and combined equity across multiple tickers.

---

## What it Does

### Data
- Fetches and normalises historical OHLC with explicit parameters to avoid API default surprises.
- Handles multi-index responses from `yfinance`.

### Indicators
- Calculates short/long SMA or EMA and ATR from high/low/close.

### Signals
- Produces **NA-safe** boolean crossover masks.
- Generates a discrete signal series that changes only on actual cross events.

### Position & Risk
- Builds a path-dependent position series with an ATR trailing stop (long-only or long/short).
- Stops and crossovers generate a detailed trade log with:
  - timestamp
  - action
  - reason
  - price
  - before/after position.

### Backtest
- Computes daily returns.
- Applies basis-point transaction costs on position changes.
- Builds an equity curve.

### Metrics
- Reports:
  - **CAGR**
  - **Sharpe (annualised)**
  - **Max Drawdown**.

### Visualisation
- Plots price with MAs, crossover markers, trailing stop lines, stop-outs, and trade markers.
- Includes:
  - an equity subplot
  - a combined equity chart for batch runs.

### Reporting
- Prints per-symbol summary tables, metrics, trade counts, and a sample of trades.
- Returns full data, metrics, and trade log for programmatic inspection.

---

## Files
| File          | Purpose |
|---------------|--------|
| `strategy.py` | Entry point to run the batch workflow. |
| `runner.py`   | Orchestrates the full pipeline for single or multiple symbols; controls printing, plotting, and returns structured results. |
| `data.py`     | Responsible for downloading OHLC and normalising the dataframe shape and columns. |
| `indicators.py` | Implements SMA/EMA and ATR computations. |
| `signals.py`  | Generates true crossover signals and boolean masks, NA-safe. |
| `stops.py`    | Applies ATR-based trailing stop logic and creates the trade log; outputs effective positions and stop diagnostics. |
| `backtest.py` | Computes strategy returns with trading costs, equity, and performance metrics. |
| `plotting.py` | Renders price with all event markers and the equity panel; supports combined equity across tickers. |

---

## Key Parameters
- **`short`, `long`**: MA windows (short must be less than long).
- **`use_ema`**: Switch between EMA and SMA.
- **`long_only`**: Choose 0/1 positions or long/short (-1/1).
- **`use_trailing_stop`, `atr_window`, `atr_mult`**: Configure the ATR trailing stop; lower multiplier tightens stops and typically increases trade frequency.
- **`cost_bps`**: Transaction costs in basis points applied to absolute position changes.
- **`plot`** and **`verbose`**: Toggle charts and console output for summaries and trade previews.

---

## Typical Outputs

### Console
- Per-symbol tail table with:
  - Close
  - ShortMA
  - LongMA
  - Signal
  - Position
  - Equity.
- Metrics line with:
  - CAGR
  - Sharpe
  - Max Drawdown.
- Total trade count and a short trade preview.

### Charts
- Price panel with crossovers, stops, and executed trade markers.
- Equity panel.
- Combined equity for batch runs.

### Programmatic Access
- Returned dictionary containing:
  - the enriched dataframe,
  - metrics,
  - and complete trade log for each symbol.
