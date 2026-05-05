
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

  ops["Revenue ($B)"] = (fin["Revenue"] / 1e3).round(2)
  ops["EBITDA ($B)"] = (fin["EBITDA"] / 1e3).round(2)
  ops["NetIncome ($B)"] = (fin["NetIncome"] / 1e3).round(2)
  ops["FCF ($B)"] = (fin["FCF"] / 1e3).round(2)

  ops["Revenue_Growth"] = rat["Revenue_Growth"].map("{:.1%}".format)
  ops["NetIncome_Growth"] = rat["NetIncome_Growth"].map("{:.1%}".format)

  ops["EBITDA_Margin"] = rat["EBITDA_Margin"].map("{:.1%}".format)
  ops["Net_Margin"] = rat["Net_Margin"].map("{:.1%}".format)
  ops["FCF_Margin"] = rat["FCF_Margin"].map("{:.1%}".format)

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

  fin, rat = latest(data, ratios, year)
  val = pd.DataFrame(index=fin.index)

  val["MarketCap ($B)"] = (fin["MarketCap"] / 1e9).round(2)
  val["EV ($B)"] = (fin["EV"] / 1e9).round(2)

  val["EV/EBITDA"] = rat["EV_EBITDA"]
  val["EV/Revenue"] = rat["EV_Revenue"]
  val["P/E"] = rat["PE"]
  val["FCF_Yield"] = rat["FCF_Yield"].map("{:.1%}".format)

  val.index = val.index.map(Company)
  val = val.round(2)

  return val

def parse_value(x):
  if isinstance(x, str):
    
    x = x.strip()
    
    if x.endswith("%"):
      return float(x[:-1]) / 100
        
    if x.endswith("x"):
      return float(x[:-1])
        
    if x == "—":
      return np.nan
        
    try:
      return float(x)
    except:
      return np.nan
  
  return x

#Peer summary
def summary(df, subject="Visa"):

  temp = df.copy()
  temp = temp.map(parse_value)

  peers = temp.drop(index=subject, errors="ignore")
  columns  = temp.select_dtypes("number").columns

  summary = pd.DataFrame({
      "Median": peers[columns].median(),
      "Mean":   peers[columns].mean(),
      "High":   peers[columns].max(),
      "Low":    peers[columns].min(),
  }).T.round(2)

  summary = summary.copy()
  
  for col in df.columns:
    if col in ["Revenue_Growth","NetIncome_Growth","EBITDA_Margin","Net_Margin","FCF_Margin","ROE", "ROA","FCF_Yield"]:
      summary[col] = summary[col].map("{:.1%}".format)
    elif col in ["NetDebtToEBITDA","FCF_Conversion"]:
      summary[col] = summary[col].map("{:.2f}x".format)
    elif col in ["InterestCoverage"]:
      summary[col] = summary[col].map("{:.1f}x".format)


  sep = pd.DataFrame([["—"] * len(df.columns)], columns=df.columns, index=["────────"])
  
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


  rows = [
      {
          "Multiple":      "EV/EBITDA",
          "Peer Median":   f"{peers['EV_EBITDA'].median():.1f}x",
          "Peer Mean":     f"{peers['EV_EBITDA'].mean():.1f}x",
          "Implied Price": ev_to_price(visa_ebitda,  peers["EV_EBITDA"].median()),
      },
      {
          "Multiple":      "EV/Revenue",
          "Peer Median":   f"{peers['EV_Revenue'].median():.1f}x",
          "Peer Mean":     f"{peers['EV_Revenue'].mean():.1f}x",
          "Implied Price": ev_to_price(visa_revenue, peers["EV_Revenue"].median()),
      },
      {
          "Multiple":      "P/E",
          "Peer Median":   f"{peers['PE'].median():.1f}x",
          "Peer Mean":     f"{peers['PE'].mean():.1f}x",
          "Implied Price": eq_to_price(visa_ni,      peers["PE"].median()),
      },
    ]

  df = pd.DataFrame(rows).set_index("Multiple")
  
  df["Current Price"] = f"${visa_price:.2f}" 
  df["Upside"] = (df["Implied Price"] / visa_price - 1).map("{:.1%}".format)
  df["Implied Price"] = df["Implied Price"].map("${:.2f}".format)

  return df.round(2)
