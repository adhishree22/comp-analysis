
import pandas as pd
import yfinance as yf

from .config import *
from .data_loader import *
from .price_loader import *


def build_dataset():

  financial_data = build_all_financials(TICKERS)
  all_data = []

  for ticker in TICKERS:
    
    income, _, _ = get_financial_statements(ticker)
    price_df = get_price_data(ticker, income)

    df = financial_data[financial_data["Ticker"] == ticker]

    df = pd.merge(df, price_df, on=["Ticker", "Year"], how="left")

    stock = yf.Ticker(ticker)

    shares = stock.info.get("sharesOutstanding", None)
    market_cap = stock.info.get("marketCap",None)

    df["Shares"] = shares
    df["MC"] = market_cap
    df["EV_s"] = stock.info.get("enterpriseValue",None)
    df["Market_Cap"] = df["Close"] * df["Shares"]

    all_data.append(df)

    print(f"{ticker} merged successfully")

    final_data = pd.concat(all_data, ignore_index=True)

    return final_data
