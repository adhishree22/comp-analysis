
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from data.config import *

sns.set_style("whitegrid")

def get_year(df, year=None):
  y = year or df["Year"].max()
  latest_year = df[df["Year"] == y]
  return latest_year

def plot_trend(df, metrics, title):

  for metric in metrics:
    plt.figure(figsize=(8, 4))
    for ticker in df["Ticker"].unique():
      subset = df[df["Ticker"] == ticker].sort_values("Year")
      plt.plot(subset["Year"], subset[metric], marker="o", label=Company.get(ticker, ticker))

    plt.title(f"{metric} — {title}")
    plt.xlabel("Year")
    plt.ylabel(metric)
    plt.legend()
    plt.tight_layout()
    plt.show()


def comparison_table(df, metrics, year=None):
  subset = get_year(df, year)
  return (subset[["Ticker"] + metrics].set_index("Ticker").rename(index=Company).sort_index().round(4))

def growth_analysis(data_df,ratio_df, year=None):

  metrics = ["Revenue", "NetIncome", "EBITDA","FCF"]
  plot_trend(data_df, metrics, "Growth Trend")

  return comparison_table(ratio_df, [m + "_Growth" for m in metrics] , year)

def margin_analysis(ratio_df, year=None):

  metrics =  ["Net_Margin", "Operating_Margin", "EBITDA_Margin", "FCF_Margin"]
  plot_trend(ratio_df, metrics , "Margin Trends")

  return comparison_table(ratio_df, metrics, year)

def cashflow_analysis(ratio_df, year=None):

  metrics = ["FCF_Conversion", "OCF_to_NetIncome", "FCF_to_EBITDA"]
  plot_trend(ratio_df,metrics, "Cash Flow Quality")

  return comparison_table(ratio_df,metrics,year)

def leverage_analysis(ratio_df, year=None):

  metrics = ["NetDebtToEBITDA", "InterestCoverage", "Debt_to_Equity"]
  plot_trend(ratio_df,metrics,"Leverage & Risk")

  return comparison_table(ratio_df,metrics, year)

def valuation_analysis(ratio_df, year=None):

  metrics= ["PE", "EV_EBITDA", "EV_Revenue", "FCF_Yield"]
  plot_trend(ratio_df, metrics, "Valuation Multiples Over Time")

  return comparison_table(ratio_df,metrics, year)

def correlation_heatmap(ratio_df):

    ratio_cols = [
        "Net_Margin", "Operating_Margin", "EBITDA_Margin", "FCF_Margin",
        "ROE", "ROA", "FCF_Conversion", "Revenue_Growth",
        "NetDebtToEBITDA", "InterestCoverage",
        "PE", "EV_EBITDA", "EV_Revenue", "FCF_Yield",
    ]
    cols = [c for c in ratio_cols if c in ratio_df.columns]

    plt.figure(figsize=(10, 7))
    sns.heatmap(
        ratio_df[cols].corr(),
        annot=True, fmt=".2f",
        cmap="RdYlGn", center=0,
        linewidths=0.5,
    )
    plt.title("Ratio Correlation Heatmap")
    plt.tight_layout()
    plt.show()


def flag_outliers(data_df,ratios_df, threshold=2.5):
  
  df = data_df.merge(ratios_df, on=["Ticker", "Year"], how="left").copy()

  cols = [
        c for c in df.columns
        if pd.api.types.is_numeric_dtype(df[c])
        and c not in ["Year"]
    ]

  z = df.groupby("Year")[cols].transform(
      lambda x: (x - x.mean()) / x.std() if x.std() > 1e-6 else x * 0
  )

  df["outlier_flag"]  = (z.abs() > threshold).any(axis=1)
  df["outlier_score"] = z.abs().max(axis=1).round(2)

  flagged = (
      df[df["outlier_flag"]]
      [["Ticker", "Year", "outlier_score"] + cols]
      .sort_values("outlier_score", ascending=False)
      .reset_index(drop=True)
  )

  return df, flagged
