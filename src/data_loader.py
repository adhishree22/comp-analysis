
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
    df["Depreciation"] = cashflow.get("Depreciation")
    df["Depreciation"]= pd.to_numeric(df["Depreciation"], errors="coerce")
    df["EBITDA"] = df["EBITDA"].fillna(df["EBIT"] + df["Depreciation"])
    df["Tax"] = income.get("Tax Provision")

    df["OCF"] = cashflow.get("Operating Cash Flow")
    df["Capex"] = abs(cashflow.get("Capital Expenditure"))
    df["FCF"] = cashflow.get("Free Cash Flow")

    df["TotalAssets"] = balance.get("Total Assets")
    df["Equity"] = balance.get("Stockholders Equity")
    df["TotalDebt"] = balance.get("Total Debt")
    df["Cash"] = balance.get("Cash And Cash Equivalents")
    df["CurrentAssets"] = balance.get("Current Assets")
    df["CurrentLiabilities"] = balance.get("Current Liabilities")
    
    df = df.apply(pd.to_numeric, errors="coerce")
    
    df = df.fillna(method="ffill", limit=1)

    if "EBIT" in df.columns:
      df["EBIT"] = df["EBIT"].fillna(income.get("Pretax Income"))

    if "CurrentAssets" in df.columns:
      df["CurrentAssets"] = df["CurrentAssets"].fillna(balance.get("Total Current Assets"))

    if "CurrentLiabilities" in df.columns:
      df["CurrentLiabilities"] = df["CurrentLiabilities"].fillna(balance.get("Total Current Liabilities"))

    if "Depreciation" in df.columns:
      df["Depreciation"] = df["Depreciation"].fillna(cashflow.get("Depreciation And Amortization"))

    if "EBITDA" in df.columns:
      ebitda = df["EBIT"] + df["Depreciation"]
      df["EBITDA"] = df["EBITDA"].fillna(ebitda)

    df = df / Scale

    df["EPS"]  = income.get("Diluted EPS")
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
