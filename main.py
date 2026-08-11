import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

DATA_DIR = Path("data")
CHART_DIR = Path("outputs/charts")
REPORT_DIR = Path("outputs/reports")
CHART_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "font.size": 10,
})


def parse_vol(v):
    # investing.com gives volume like "5.02M" or "440.86K", sometimes just blank
    if pd.isna(v) or v == "":
        return np.nan
    v = str(v).strip()
    if v.endswith("M"):
        return float(v[:-1]) * 1_000_000
    elif v.endswith("K"):
        return float(v[:-1]) * 1_000
    else:
        try:
            return float(v)
        except:
            return np.nan


def load_csv(path, date_fmt):
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    df["Date"] = pd.to_datetime(df["Date"], format=date_fmt)
    df = df.rename(columns={"Price": "Close"})

    # these come in as strings with commas like "24,677.00", pandas won't parse that directly
    for col in ["Open", "High", "Low", "Close"]:
        df[col] = df[col].astype(str).str.replace(",", "")
        df[col] = df[col].astype(float)

    df["Volume"] = df["Vol."].apply(parse_vol)
    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]
    df = df.sort_values("Date").reset_index(drop=True)
    return df


print("loading data...")
nifty = load_csv(DATA_DIR / "nifty_50.csv", "%d-%m-%Y")
crude = load_csv(DATA_DIR / "crude_oil.csv", "%m/%d/%Y")
print("got the data, nifty rows:", len(nifty), "crude rows:", len(crude))

instruments = {
    "Nifty Futures": nifty,
    "Crude Oil Futures": crude,
}

report_lines = ["# Futures Market Trend Analysis\n"]

for name, data in instruments.items():
    print("\n----", name, "----")

    df = data.copy()
    df["Daily_Return"] = df["Close"].pct_change()
    df["Log_Return"] = np.log(df["Close"] / df["Close"].shift(1))

    df["MA_5"] = df["Close"].rolling(5).mean()
    df["MA_20"] = df["Close"].rolling(20).mean()

    df["Volatility_20"] = df["Daily_Return"].rolling(20).std()
    df["Volatility_20_Annualized"] = df["Volatility_20"] * np.sqrt(252)

    # crossover detection, basically golden cross / death cross logic
    valid = df.dropna(subset=["MA_5", "MA_20"]).copy()
    valid["diff"] = valid["MA_5"] - valid["MA_20"]
    valid["prev_diff"] = valid["diff"].shift(1)

    signals = []
    for i, row in valid.iterrows():
        if pd.isna(row["prev_diff"]):
            continue
        if row["prev_diff"] <= 0 and row["diff"] > 0:
            signals.append((row["Date"], row["Close"], "Golden Cross"))
        elif row["prev_diff"] >= 0 and row["diff"] < 0:
            signals.append((row["Date"], row["Close"], "Death Cross"))
    crossovers = pd.DataFrame(signals, columns=["Date", "Close", "Signal"])

    print("reversals found:", len(crossovers))

    # this threshold felt right after looking at the last couple years of data
    vol_threshold = df["Volatility_20"].quantile(0.90)
    df["High_Volatility"] = df["Volatility_20"] >= vol_threshold

    returns = df["Daily_Return"].dropna()
    stats = {}
    stats["Mean Daily Return %"] = round(returns.mean() * 100, 4)
    stats["Std Dev Daily Return %"] = round(returns.std() * 100, 4)
    stats["Annualized Return %"] = round(((1 + returns.mean()) ** 252 - 1) * 100, 2)
    stats["Annualized Volatility %"] = round(returns.std() * np.sqrt(252) * 100, 2)
    stats["Best Day %"] = round(returns.max() * 100, 2)
    stats["Worst Day %"] = round(returns.min() * 100, 2)
    stats["Skew"] = round(returns.skew(), 3)
    stats["Kurtosis"] = round(returns.kurt(), 3)
    stats["Positive Days %"] = round((returns > 0).mean() * 100, 2)
    stats["Negative Days %"] = round((returns < 0).mean() * 100, 2)

    for k, v in stats.items():
        print(k, ":", v)

    print("saving charts...")
    stub = name.lower().replace(" ", "_")

    fig, ax = plt.subplots(figsize=(13, 6))
    ax.plot(df["Date"], df["Close"], color="#1f2937", linewidth=1.1, label="Close Price")
    ax.plot(df["Date"], df["MA_5"], color="#2563eb", linewidth=1.3, label="MA_5")
    ax.plot(df["Date"], df["MA_20"], color="#dc2626", linewidth=1.3, label="MA_20")
    if len(crossovers) > 0:
        golden = crossovers[crossovers["Signal"] == "Golden Cross"]
        death = crossovers[crossovers["Signal"] == "Death Cross"]
        ax.scatter(golden["Date"], golden["Close"], marker="^", color="#16a34a", s=100, zorder=5, label="Golden Cross")
        ax.scatter(death["Date"], death["Close"], marker="v", color="#b91c1c", s=100, zorder=5, label="Death Cross")
    ax.set_title(name + " - Price with MA_5/MA_20 and Trend Reversals", fontsize=13, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc="upper left", fontsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(CHART_DIR / (stub + "_price_ma.png"), dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(13, 4.5))
    ax.plot(df["Date"], df["Volatility_20"], color="#7c3aed", linewidth=1.1, label="Rolling Volatility")
    ax.axhline(vol_threshold, color="#b91c1c", linestyle="--", linewidth=1, label="High Vol Threshold")
    high_vol_days = df[df["Volatility_20"] >= vol_threshold]
    ax.scatter(high_vol_days["Date"], high_vol_days["Volatility_20"], color="#b91c1c", s=15, zorder=5)
    ax.set_title(name + " - Rolling Volatility", fontsize=13, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Std Dev of Returns")
    ax.legend(loc="upper left", fontsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(CHART_DIR / (stub + "_volatility.png"), dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    ret_pct = df["Daily_Return"].dropna() * 100
    ax.hist(ret_pct, bins=30, color="#0891b2", alpha=0.85, edgecolor="white")
    ax.axvline(ret_pct.mean(), color="#dc2626", linestyle="--", linewidth=1.3, label=f"Mean: {ret_pct.mean():.3f}%")
    ax.set_title(name + " - Daily Returns Distribution", fontsize=13, fontweight="bold")
    ax.set_xlabel("Daily Return %")
    ax.set_ylabel("Frequency")
    ax.legend()
    fig.tight_layout()
    fig.savefig(CHART_DIR / (stub + "_returns_dist.png"), dpi=150)
    plt.close(fig)

    df.to_csv(REPORT_DIR / (stub + "_processed.csv"), index=False)
    crossovers.to_csv(REPORT_DIR / (stub + "_reversals.csv"), index=False)

    report_lines.append("## " + name + "\n")
    report_lines.append("Period: " + str(df["Date"].min().date()) + " to " + str(df["Date"].max().date()) + " (" + str(len(df)) + " rows)\n")

    report_lines.append("### Trend Reversals")
    report_lines.append("- Total: " + str(len(crossovers)))
    report_lines.append("- Golden Crosses: " + str((crossovers["Signal"] == "Golden Cross").sum()))
    report_lines.append("- Death Crosses: " + str((crossovers["Signal"] == "Death Cross").sum()))

    report_lines.append("\n### Stats")
    report_lines.append("| Metric | Value |")
    report_lines.append("|---|---|")
    for k, v in stats.items():
        report_lines.append("| " + k + " | " + str(v) + " |")

    if len(crossovers) > 0:
        report_lines.append("\n### Reversal Dates")
        report_lines.append("| Date | Close | Signal |")
        report_lines.append("|---|---|---|")
        for _, row in crossovers.iterrows():
            report_lines.append("| " + str(row["Date"].date()) + " | " + str(round(row["Close"], 2)) + " | " + row["Signal"] + " |")

    report_lines.append("")

# TODO: maybe add volume later, could be useful for confirming breakouts / spikes
with open(REPORT_DIR / "summary_report.md", "w") as f:
    f.write("\n".join(report_lines))

print("\ndone, check outputs/charts and outputs/reports")
