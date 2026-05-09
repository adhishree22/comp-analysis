
import pandas as pd

from data.config import *

def safe_divide(a, b):
    return a.div(b.replace(0, float("nan")))

def add_ratios(df):

    df = df.sort_values(["Ticker", "Year"]).reset_index(drop=True)

    ratios = pd.DataFrame()
    ratios["Ticker"] = df["Ticker"]
    ratios["Year"]   = df["Year"]

    for col in ["Revenue", "NetIncome", "EBITDA", "EBIT","FCF"]:
      ratios[f"{col}_Growth"] = df.groupby("Ticker")[col].pct_change()

    ratios["Net_Margin"] = safe_divide(df["NetIncome"], df["Revenue"])
    ratios["Operating_Margin"] = safe_divide(df["EBIT"], df["Revenue"])
    ratios["EBITDA_Margin"] = safe_divide(df["EBITDA"], df["Revenue"])
    ratios["FCF_Margin"] = safe_divide(df["FCF"], df["Revenue"])
    ratios["ROE"] = safe_divide(df["NetIncome"], df["Equity"])
    ratios["ROA"] = safe_divide(df["NetIncome"], df["TotalAssets"])

    ratios["Incremental_Operating_Margin"] = safe_divide(df.groupby("Ticker")["EBIT"].diff() , df.groupby("Ticker")["Revenue"].diff())
    ratios["Incremental_EBITDA_Margin"] = safe_divide(df.groupby("Ticker")["EBITDA"].diff() , df.groupby("Ticker")["Revenue"].diff())
    ratios["Incremental_Net_Margin"] = safe_divide(df.groupby("Ticker")["NetIncome"].diff() , df.groupby("Ticker")["Revenue"].diff())
    ratios["Incremental_FCF_Margin"] = safe_divide(df.groupby("Ticker")["FCF"].diff() , df.groupby("Ticker")["Revenue"].diff())


    ratios["FCF_Conversion"] = safe_divide(df["FCF"],  df["NetIncome"])
    ratios["OCF_to_NetIncome"] = safe_divide(df["OCF"],  df["NetIncome"])
    ratios["FCF_to_EBITDA"] = safe_divide(df["FCF"],  df["EBITDA"])

    ratios["Debt_to_Equity"] = safe_divide(df["TotalDebt"], df["Equity"])
    ratios["DebtToEBITDA"] = safe_divide(df["TotalDebt"], df["EBITDA"])
    ratios["InterestCoverage"] = safe_divide(df["EBIT"], df["Interest"])
    ratios["NetDebtToEBITDA"] = safe_divide(df["NetDebt"],   df["EBITDA"])

    ratios["PE"] = safe_divide(df["MarketCap"], (df["NetIncome"] * Scale))
    ratios["EV_EBITDA"] = safe_divide(df["EV"], (df["EBITDA"] * Scale))
    ratios["EV_Revenue"]     = safe_divide(df["EV"], (df["Revenue"] * Scale))
    ratios["FCF_Yield"] = safe_divide((df["FCF"] * Scale), df["MarketCap"])

    ratios["Earnings_Volatility"] = ratios.groupby("Ticker")["NetIncome_Growth"].transform("std")

    ratios.replace([float("inf"), -float("inf")], float("nan"), inplace=True)
    ratios = ratios.round(4)

    return ratios
