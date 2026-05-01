
import pandas as pd

def safe_divide(a, b):
    return a.div(b.replace(0, float("nan")))

def add_ratios(df):

    df = df.copy()

    df = df.sort_values(["Ticker", "Year"]).reset_index(drop=True)

    df.replace([float("inf"), -float("inf")], None, inplace=True)

    for col in ["Revenue", "NetIncome", "EBITDA", "EBIT","FCF"]:
      df[f"{col}_Growth"] = df.groupby("Ticker")[col].pct_change()

    df["Net_Margin"] = safe_divide(df["NetIncome"], df["Revenue"])
    df["Operating_Margin"] = safe_divide(df["EBIT"], df["Revenue"])
    df["EBITDA_Margin"] = safe_divide(df["EBITDA"], df["Revenue"])
    df["FCF_Margin"] = safe_divide(df["FCF"], df["Revenue"])
    df["ROE"] = safe_divide(df["NetIncome"], df["Equity"])
    df["ROA"] = safe_divide(df["NetIncome"], df["TotalAssets"])

    df["Incremental_Operating_Margin"] = safe_divide(df.groupby("Ticker")["EBIT"].diff() , df.groupby("Ticker")["Revenue"].diff())
    df["Incremental_EBITDA_Margin"] = safe_divide(df.groupby("Ticker")["EBITDA"].diff() , df.groupby("Ticker")["Revenue"].diff())
    df["Incremental_Net_Margin"] = safe_divide(df.groupby("Ticker")["NetIncome"].diff() , df.groupby("Ticker")["Revenue"].diff())
    df["Incremental_FCF_Margin"] = safe_divide(df.groupby("Ticker")["FCF"].diff() , df.groupby("Ticker")["Revenue"].diff())


    df["FCF_Conversion"] = safe_divide(df["FCF"],  df["NetIncome"])
    df["OCF_to_NetIncome"] = safe_divide(df["OCF"],  df["NetIncome"])
    df["FCF_to_EBITDA"] = safe_divide(df["FCF"],  df["EBITDA"])

    df["Debt_to_Equity"] = safe_divide(df["TotalDebt"], df["Equity"])
    df["DebtToEBITDA"] = safe_divide(df["TotalDebt"], df["EBITDA"])
    df["InterestCoverage"] = safe_divide(df["EBIT"], df["Interest"])
    df["NetDebtToEBITDA"] = safe_divide(df["NetDebt"],   df["EBITDA"])

    df["PE"] = safe_divide(df["MarketCap"], df["NetIncome"])
    df["EV_EBITDA"] = safe_divide(df["EV"], df["EBITDA"])
    df["EV_Revenue"]     = safe_divide(df["EV"],        df["Revenue"])
    df["FCF_Yield"] = safe_divide(df["FCF"], df["MarketCap"])

    df["Earnings_Volatility"] = df.groupby("Ticker")["NetIncome_Growth"].transform(lambda x: x.rolling(3).std())

    df.replace([float("inf"), -float("inf")], float("nan"), inplace=True)
    df = df.round(4)

    return df
