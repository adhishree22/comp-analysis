
import yfinance as yf
import pandas as pd

from .config import *


def get_price_data(ticker, income):

    start_year = income.index.year.min()
    end_year = income.index.year.max()

    if ticker in Fiscal_Year_End:
        fiscal_end = Fiscal_Year_End[ticker]
    else:
        fiscal_end = Default_Fiscal_Year

    try:
        price_data = yf.download(
            ticker,
            start=f"{start_year}-01-01",
            end=f"{end_year}-{fiscal_end}",
            auto_adjust=True,
            progress=False
        )
    except Exception as e:
        raise ValueError(f"Error downloading price data for {ticker}: {e}")


    if isinstance(price_data.columns, pd.MultiIndex):
        price_data.columns = price_data.columns.droplevel(1)
    price_data = price_data.reset_index()
    price_data["Date"] = pd.to_datetime(price_data["Date"])#.dt.tz_localize(None)
    price_data["Year"] = price_data["Date"].dt.year

    yearly_prices = (price_data.groupby("Year")["Close"].last().reset_index())
    yearly_prices["Ticker"] = ticker

    return yearly_prices


def build_all_prices(tickers, income_map):

    all_prices = []

    for ticker in tickers:
        try:
            income = income_map[ticker]
            price_df = get_price_data(ticker, income)
            all_prices.append(price_df)
            print(f"{ticker} prices loaded")
        except Exception as e:
            print(f"{ticker} price failed: {e}")

    final_price = pd.concat(all_prices, ignore_index=True)

    return final_price
