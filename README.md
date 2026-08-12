# Futures Market Trend Analysis

This project analyzes historical price data for Nifty 50 Futures and Crude Oil (WTI) Futures to study market trends using moving averages and volatility.

## Overview

The idea was to look at how these two markets behave over time - when they trend, when they reverse, and how volatile they get around major events. I used monthly historical data for both instruments and applied a few standard technical analysis techniques to pull out patterns.

## What's in this project

- 5-period and 20-period moving averages calculated on closing price
- Daily returns (simple and log returns)
- Rolling volatility using standard deviation of returns, annualized for comparison
- Trend reversal detection using moving average crossovers (Golden Cross and Death Cross)
- Flagging of high volatility periods (top 10% most volatile)
- Charts for price with moving averages, volatility over time, and return distributions
- A summary report with all the stats and detected reversal dates

## Project structure

```
futures_trend_analysis/
├── main.py
├── requirements.txt
├── data/
│   ├── nifty_50.csv
│   └── crude_oil.csv
└── outputs/
    ├── charts/
    └── reports/
```

## Data

The data is included in the repo under `data/`.

- `Nifty 50 daily data .csv` - Nifty 50 Futures, monthly data from Feb 2022 to Aug 2026
- `Crude Oil WTI Futures Historical Data.csv` - Crude Oil (WTI) Futures, monthly data from Aug 2022 to Aug 2026

Both were pulled from Investing.com's historical data export, with columns Date, Price, Open, High, Low, Vol., and Change %. The Price column is treated as the closing price for each period.

If you want to update it with more recent data, just export a fresh CSV from Investing.com and replace the file in the data folder - the column format needs to stay the same.

## How to run it

```
pip install -r requirements.txt
python main.py
```

This reads the CSVs, computes all the indicators, runs the trend reversal detection, and generates the charts and report. Charts go to `outputs/charts/` and the processed data plus the summary report go to `outputs/reports/`.

## Some notes on the results

Both datasets are Daily based, which was intentional so the two instruments could be compared on the same timeframe. 

Crude oil showed a lot more volatility than Nifty over this period, which lines up with what you'd expect given how sensitive oil prices are to supply shocks and geopolitical events. Nifty had fewer trend reversals overall, more of a steady uptrend with a couple of sharp corrections.

## Possible extensions

- Add exponential moving averages instead of simple ones
- Try different MA window pairs like 10/50 instead of 5/20
- Overlay specific known events (rate hikes, wars, OPEC decisions) as markers on the charts
- Extend to daily data if a longer daily history becomes available
