
import pandas as pd
import numpy as np

from src.config import *

def _latest(data, ratios, year=None):
  y = year or data["Year"].max()
  fin = data[data["Year"] == y].set_index("Ticker")
  rat = ratios[ratios["Year"] == y].set_index("Ticker")
  
  return fin, rat

#How the businesses actually perform
#Answers: who runs the better business?
def operating_comparison(data, ratios, year=None):
  
  fin, rat = _latest(data, ratios, year)
  ops = pd.DataFrame(index=fin.index)

  ops["Revenue"] = fin["Revenue"] * Scale
  ops["EBITDA"] = fin["EBITDA"] * Scale
  ops["NetIncome"] = fin["NetIncome"] * Scale
  ops["FCF"] = fin["FCF"] * Scale

  ops["Rev_Growth"] = rat["Revenue_Growth"].map("{:.1%}".format)
  ops["NI_Growth"] = rat["NetIncome_Growth"].map("{:.1%}".format)

  ops["EBITDA Margin"] = rat["EBITDA_Margin"].map("{:.1%}".format)
  ops["Net Margin"] = rat["Net_Margin"].map("{:.1%}".format)
  ops["FCF Margin"] = rat["FCF_Margin"].map("{:.1%}".format)
  
  ops["ROE"] = rat["ROE"].map("{:.1%}".format)
  ops["ROA"] = rat["ROA"].map("{:.1%}".format)

  ops["FCF_Conversion"] = rat["FCF_Conversion"].map("{:.2f}x".format)

  ops["NetDebtToEBITDA"] = rat["NetDebtToEBITDA"].map("{:.2f}x".format)
  ops["InterestCoverage"] = rat["InterestCoverage"].map("{:.1f}x".format)

  ops.index = ops.index.map(Company)
	ops = ops.round(2)
 
  return ops


#How the market prices each business
#Answers: how expensive is each company relative to peers?
def valuation_comparison(data, ratios, year=None):
  
  fin, rat = _latest(data, ratios, year)
  val = pd.DataFrame(index=fin.index)

  val["MarketCap"] = fin["MarketCap"]
  val["EV"] = fin["EV"]

  val["EV/EBITDA"] = rat["EV_EBITDA"]
  val["EV/Revenue"] = rat["EV_Revenue"]
  val["P/E"] = rat["PE"]
  val["FCF Yield"] = rat["FCF_Yield"].map("{:.1%}".format)

  val.index = val.index.map(Company)
  val = val.round(2)

  return val


#Peer summary
def add_summary_rows(df, subject="Visa"):
  
  peers        = df.drop(index=subject, errors="ignore")
  numeric_cols = df.select_dtypes("number")

  summary = pd.DataFrame({
      "Median": peers[numeric_cols].median().round(1),
      "Mean":   peers[numeric_cols].mean().round(1),
      "High":   peers[numeric_cols].max().round(1),
      "Low":    peers[numeric_cols].min().round(1),
  }).T.round(2)

  data = pd.concat([df, summary])
  
  return data


#Implied Valuation
#What Visa should be worth using peer multiples
def implied_valuation(data, ratios, year=None):
  
  fin, rat = _latest(data, ratios, year)
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
        "EV/EBITDA": ev_price(ebitda, peers["EV_EBITDA"].median()),
        "EV/Revenue": ev_price(revenue, peers["EV_Revenue"].median()),
        "P/E": eq_price(ni, peers["PE"].median()),
    }

    df = pd.DataFrame.from_dict(results, orient="index", columns=["Implied Price"])

    df["Current"] = price
    df["Upside"] = (df["Implied Price"] / price - 1)

  return df.round(2)
