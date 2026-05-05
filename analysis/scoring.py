
import pandas as pd
import numpy as np
from src.config import *


def latest_df(ratios, year=None):
  
  y = year or ratios["Year"].max()
  latest = ratios[ratios["Year"] == y].set_index("Ticker")

  return latest

def normalize(series):
    denom = series.max() - series.min()
    if denom == 0:
        return series * 0 + 0.5
    return (series - series.min()) / denom

def quality_score(ratios, year=None):

    #Higher = better business fundamentals.
    latest = latest_df(ratios, year)
    scores = pd.DataFrame(index=latest.index)

    #Profitability — higher is better
    scores["Profitability"] = (
        0.4 * normalize(latest["Net_Margin"]) +
        0.3 * normalize(latest["EBITDA_Margin"]) +
        0.3 * normalize(latest["FCF_Margin"])
    )

    #Returns — higher is better
    scores["Returns"] = (
        0.6 * normalize(latest["ROA"]) +              #efficeincy
        0.4 * normalize(latest["FCF_Conversion"])     #earnings quality
    )

    #Balance Sheet — lower leverage = better
    scores["Balance_Sheet"] = (
        0.5 * normalize(-latest["NetDebtToEBITDA"]) +
        0.5 * normalize(latest["InterestCoverage"])
    )

    scores = scores.round(2)
    for col in scores.columns:
        scores[col] = scores[col].clip(0, 1)

    """
    Profitability (45%) - business model strength
    Returns (30%) - efficiency, earnings quality
    Balance Sheet (25%) - low leverage
    """
    #Weighted composite
    scores["Quality_Score"] = (
        0.45 * scores["Profitability"] +
        0.30 * scores["Returns"] +
        0.25 * scores["Balance_Sheet"] 
    ) * 100

    scores["Quality_Score"] = scores["Quality_Score"].clip(0, 100).round(2)
    scores.index = scores.index.map(Company)

    return scores

def risk_score(ratios, year=None):

    #Higher = more risky.    
    latest = latest_df(ratios, year)
    scores = pd.DataFrame(index=latest.index)

    #Leverage risk — higher debt = more risk
    scores["Leverage_Risk"] = (
        0.5 * normalize(latest["NetDebtToEBITDA"].clip(lower=0)) +
        0.5 * normalize(latest["Debt_to_Equity"].clip(lower=0))
    )

    #Coverage risk — lower coverage = more risk
    scores["Coverage_Risk"] = normalize(
        1 / latest["InterestCoverage"].replace(0, np.nan)
    )

    #Earnings stability — higher volatility = more risk
    scores["Earnings_Risk"] = normalize(latest["Earnings_Volatility"])

    scores = scores.round(2)
    for col in scores.columns:
        scores[col] = scores[col].clip(0, 1)

    """
    Leverage (40%) - leverage is the primary risk driver
    Coverage (30%) - default risk
    Earnings Volatility (30%) - Penalizes unstable businesses
    """
    scores["Risk_Score"] = (
        0.40 * scores["Leverage_Risk"] +
        0.30 * scores["Coverage_Risk"] +
        0.30 * scores["Earnings_Risk"]
    ) * 100

    scores["Risk_Score"]   = scores["Risk_Score"].clip(0, 100).round(2)
    scores["Safety_Score"] = (100 - scores["Risk_Score"]).round(2)

    scores.index = scores.index.map(Company)
    return scores

def growth_score(ratios, year=None):

    #Higher = faster and more consistent growth.
    latest = latest_df(ratios, year)
    scores = pd.DataFrame(index=latest.index)

    # Revenue growth — top line expansion
    scores["Revenue_Growth"]   = normalize(latest["Revenue_Growth"])

    # Earnings growth — bottom line expansion  
    scores["Earnings_Growth"]  = normalize(latest["NetIncome_Growth"])

    # FCF growth — cash generation expansion
    scores["FCF_Growth"]       = normalize(latest["FCF_Growth"])

    # Consistency — lower volatility = more consistent grower
    # Invert so lower volatility scores higher
    scores["Consistency"]      = normalize(-latest["Earnings_Volatility"])

    scores = scores.round(2)
    for col in scores.columns:
        scores[col] = scores[col].clip(0, 1)

    """
    Revenue (35%) - Pure demand
    Earnings (30%) - Operational leverage
    FCF Growth (20%) - Real cash growth
    Consistency (15%) - Based on volatility
    """
    scores["Growth_Score"] = (
        0.35 * scores["Revenue_Growth"] +
        0.30 * scores["Earnings_Growth"] +
        0.20 * scores["FCF_Growth"] +
        0.15 * scores["Consistency"]
    ) * 100

    scores["Growth_Score"] = scores["Growth_Score"].clip(0, 100).round(2)
    scores.index = scores.index.map(Company)

    return scores

def composite_score(ratios, year=None):

    quality = quality_score(ratios, year)
    risk = risk_score(ratios, year)
    growth = growth_score(ratios, year)

    composite_score = pd.DataFrame(index=quality.index)
    composite_score["Quality_Score"] = quality["Quality_Score"]
    composite_score["Growth_Score"]  = growth["Growth_Score"]
    composite_score["Risk_Score"]    = risk["Risk_Score"]
    composite_score["Safety_Score"]  = risk["Safety_Score"]

    """
    Quality (45%) → Drives long-term compounding
    Growth (30%) → Enhances valuation upside
    Safety (25%) → Prevents blow-ups, but not over-prioritized
    """
    composite_score["Composite"] = (
        0.45 * composite_score["Quality_Score"] +
        0.30 * composite_score["Growth_Score"] +
        0.25 * composite_score["Safety_Score"]
    ).round(2)

    composite_score = composite_score.sort_values("Composite", ascending=False)

    def label(score):
        if score >= 65: return "Strong"
        elif score >= 50: return "Moderate"
        else: return "Weak"

    composite_score["Assessment"] = composite_score["Composite"].apply(label)

    return composite_score
