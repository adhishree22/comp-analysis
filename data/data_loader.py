
import yfinance as yf
import pandas as pd

from .config import *


def get_financial_statements(ticker):

    stock = yf.Ticker(ticker)

    try:
        income = stock.financials.T.sort_index().drop_duplicates()
        balance = stock.balance_sheet.T.sort_index().drop_duplicates()
        cashflow = stock.cashflow.T.sort_index().drop_duplicates()
    except Exception as e:
        raise ValueError(f"Error fetching data for {ticker}: {e}")


    income = income.iloc[:5]
    balance = balance.iloc[:5]
    cashflow = cashflow.iloc[:5]

    return income, balance, cashflow


def build_financial_dataframe(ticker):

    income, balance, cashflow = get_financial_statements(ticker)

    df = pd.DataFrame(index=income.index)

    df["Revenue"] = income.get("Total Revenue")
    df["NetIncome"] = income.get("Net Income")
    df["EBIT"] = income.get("Operating Income")
    df["EBITDA"] = income.get("EBITDA")
    df["Interest"] = income.get("Interest Expense")
    df["Tax"] = income.get("Tax Provision")

    df["OCF"] = cashflow.get("Operating Cash Flow")
    df["Capex"] = abs(cashflow.get("Capital Expenditure"))
    df["FCF"] = cashflow.get("Free Cash Flow")
    df["Depreciation"]  = cashflow.get("Depreciation And Amortization")

    df["TotalAssets"] = balance.get("Total Assets")
    df["Equity"] = balance.get("Stockholders Equity")
    df["TotalDebt"] = balance.get("Total Debt")
    df["Cash"] = balance.get("Cash And Cash Equivalents")

    df = df.apply(pd.to_numeric, errors="coerce")

    if df["EBIT"].isna().any():
       df["EBIT"] = df["EBIT"].fillna(income.get("Pretax Income") + df["Interest"].abs())

    if "Depreciation" in df.columns:
      df["Depreciation"] = df["Depreciation"].fillna(cashflow.get("Depreciation And Amortization"))

    df["EBITDA_computed"] = df["EBIT"] + df["Depreciation"]
    df["EBITDA"] = df[["EBITDA", "EBITDA_computed"]].max(axis=1)
    df.drop(columns=["EBITDA_computed"], inplace=True)

    if df["EBITDA"].isna().any():
      df["EBITDA"] = df["EBITDA"].fillna(df["EBIT"] + df["Depreciation"])

    if df["Capex"].isna().any():
      df["Capex"] = df["Capex"].fillna(0)

    df = df / Scale

    df["EPS"]  = (income.get("Diluted EPS")).round(2)
    df["Shares"] = balance.get("Ordinary Shares Number")
    df["Ticker"] = ticker
    df["Year"] = df.index.year

    return df.reset_index(drop=True)


def build_all_financials(tickers):

    all_data = []

    for ticker in tickers:
        try:
            df = build_financial_dataframe(ticker)
            all_data.append(df)
            print(f"{ticker} loaded")
        except Exception as e:
            print(f"{ticker} failed: {e}")

    final_data = pd.concat(all_data, ignore_index=True)
    final_data = final_data.dropna(subset=["Revenue"],how="all")

    return final_data
