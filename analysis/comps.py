
import pandas as pd
import numpy as np

from src.config import *

def latest(data, ratios, year=None):
  y = year or data["Year"].max()
  fin = data[data["Year"] == y].set_index("Ticker")
  rat = ratios[ratios["Year"] == y].set_index("Ticker")

  return fin, rat

#How the businesses actually perform
#Answers: who runs the better business?
def operating_comparison(data, ratios, year=None):

  fin, rat = latest(data, ratios, year)
  ops = pd.DataFrame(index=fin.index)

  ops["Revenue"] = fin["Revenue"] * Scale
  ops["EBITDA"] = fin["EBITDA"] * Scale
  ops["NetIncome"] = fin["NetIncome"] * Scale
  ops["FCF"] = fin["FCF"] * Scale

  ops["Revenue_Growth"] = rat["Revenue_Growth"]
  ops["NetIncome_Growth"] = rat["NetIncome_Growth"]

  ops["EBITDA_Margin"] = rat["EBITDA_Margin"]
  ops["Net_Margin"] = rat["Net_Margin"]
  ops["FCF_Margin"] = rat["FCF_Margin"]

  ops["ROE"] = rat["ROE"]
  ops["ROA"] = rat["ROA"]

  ops["FCF_Conversion"] = rat["FCF_Conversion"]

  ops["NetDebtToEBITDA"] = rat["NetDebtToEBITDA"]
  ops["InterestCoverage"] = rat["InterestCoverage"]

  ops.index = ops.index.map(Company)
  ops = ops.round(2)

  return ops


#How the market prices each business
#Answers: how expensive is each company relative to peers?
def valuation_comparison(data, ratios, year=None):

  fin, rat = latest(data, ratios, year)
  val = pd.DataFrame(index=fin.index)

  val["MarketCap"] = fin["MarketCap"]
  val["EV"] = fin["EV"]

  val["EV/EBITDA"] = rat["EV_EBITDA"]
  val["EV/Revenue"] = rat["EV_Revenue"]
  val["P/E"] = rat["PE"]
  val["FCF_Yield"] = rat["FCF_Yield"]

  val.index = val.index.map(Company)
  val = val.round(2)

  return val


#Peer summary
def summary(df, subject="Visa"):

  peers        = df.drop(index=subject, errors="ignore")
  columns = df.select_dtypes("number").columns

  summary = pd.DataFrame({
      "Median": peers[columns].median(),
      "Mean":   peers[columns].mean(),
      "High":   peers[columns].max(),
      "Low":    peers[columns].min(),
  }).T.round(2)

  sep = pd.DataFrame([["—"] * len(df.columns)], columns=df.columns, index=[""])
  
  data = pd.concat([df, sep, summary])

  return data


#Implied Valuation
#What Visa should be worth using peer multiples
def implied_valuation(data, ratios, year=None):

  fin, rat = latest(data, ratios, year)
  peers = rat.drop(index="V")

  visa_ebitda  = fin.loc["V", "EBITDA"]
  visa_revenue = fin.loc["V", "Revenue"]
  visa_ni = fin.loc["V", "NetIncome"]
  visa_netdebt = fin.loc["V", "NetDebt"]
  visa_shares = fin.loc["V", "Shares"]
  visa_price = fin.loc["V", "Close"]

  def ev_to_price(metric, multiple):
    return ((metric * Scale * multiple) - (visa_netdebt * Scale)) / visa_shares

  def eq_to_price(metric, multiple):
    return (metric * Scale * multiple) / visa_shares


  results = {
      "EV/EBITDA": ev_to_price(visa_ebitda, peers["EV_EBITDA"].median()),
      "EV/Revenue": ev_to_price(visa_revenue, peers["EV_Revenue"].median()),
      "P/E": eq_to_price(visa_ni, peers["PE"].median()),
  }

  df = pd.DataFrame.from_dict(results, orient="index", columns=["Implied Price"])

  df["Current"] = visa_price
  df["Upside"] = (df["Implied Price"] / visa_price - 1)

  return df.round(2)
