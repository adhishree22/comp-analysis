
import pandas as pd
import yfinance as yf

from .config import *
from .data_loader import *
from .price_loader import *


def build_dataset():

    all_data = []

    for ticker in TICKERS:

      financial_df = build_all_financials([ticker])
      income, _, _ = get_financial_statements(ticker)

      price_df = get_price_data(ticker, income)

      df = pd.merge(financial_df, price_df, on=["Ticker", "Year"], how="left")

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
