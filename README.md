Futures Market Trend Analysis
This project analyzes historical price data for Nifty 50 Futures and Crude Oil (WTI) Futures to study market trends using moving averages and volatility.

Overview
The idea was to look at how these two markets behave over time - when they trend, when they reverse, and how volatile they get around major events. I'm using daily historical data for both instruments and applying a few standard technical analysis techniques to pull out patterns.

What's in this project
5-day and 20-day moving averages calculated on closing price
Daily returns (simple and log returns)
Rolling volatility using standard deviation of returns, annualized for comparison
Trend reversal detection using moving average crossovers (Golden Cross and Death Cross)
Flagging of high volatility periods (top 10% most volatile)
Charts for price with moving averages, volatility over time, and return distributions
A summary report with all the stats and detected reversal dates
Project structure
futures_trend_analysis/
├── main.py
├── requirements.txt
├── data/
│   ├── nifty_50.csv
│   └── crude_oil.csv
└── outputs/
    ├── charts/
    └── reports/
Data
The data is included in the repo under data/.

nifty_50.csv - Nifty 50 Futures, daily data, roughly 1155 rows, Jan 2022 to Aug 2026
crude_oil.csv - Crude Oil (WTI) Futures, daily data, roughly 1205 rows, Jan 2022 to Aug 2026
Both were pulled from Investing.com's historical data export, with columns Date, Price, Open, High, Low, Vol., and Change %. The Price column is treated as the closing price for each day.

If you want to update it with more recent data, just export a fresh CSV from Investing.com and replace the file in the data folder - the column format needs to stay the same.

How to run it
pip install -r requirements.txt
python main.py
This reads the CSVs, computes all the indicators, runs the trend reversal detection, and generates the charts and report. Charts go to outputs/charts/ and the processed data plus the summary report go to outputs/reports/.

Some notes on the results
Switching from monthly to daily data changed things quite a bit. With ~1150+ rows for each instrument now, the 20-day MA actually has enough history behind it from pretty early on, unlike before when it barely showed up on the chart.

Crude oil is clearly more volatile than Nifty over this period, which isn't surprising given how sensitive oil is to supply shocks and geopolitical stuff - you can see it in the annualized volatility numbers and just by eyeballing the price chart, it swings a lot harder.

One thing I noticed is that MA 5/20 gets pretty noisy on daily data. There are a lot of crossovers, especially during choppy periods, and a good chunk of them don't really represent a meaningful trend reversal - the price just wiggles across the MA lines back and forth for a few days. On monthly data the crossovers felt more meaningful, on daily data there's just more signal and more noise mixed together.

Also worth being honest about: this is still a fairly basic approach. It doesn't account for volume, doesn't try to filter out noisy/whipsaw crossovers, and doesn't compare against any kind of benchmark or baseline strategy. It's more of a descriptive/exploratory look at trend and volatility patterns than anything close to a trading signal.

Possible extensions
Filter out crossovers that reverse again within a few days (reduce whipsaw noise)
Try longer MA windows like 10/50 or 20/50, which might be less noisy on daily data
Add exponential moving averages instead of simple ones
Overlay specific known events (rate hikes, wars, OPEC decisions) as markers on the charts
Bring in volume to see if it confirms or contradicts the price-based signals
