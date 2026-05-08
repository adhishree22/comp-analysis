
import pandas as pd
from data.config import *
from data.beta_loader import *

def build_risk_scorecard(data_df, ratios_df, year=None):

    y = year or data_df["Year"].max()
    latest = data_df[data_df["Year"] == y].set_index("Ticker").copy()
    latest_ratios = ratios_df[ratios_df["Year"] == y].set_index("Ticker").copy()

    betas = get_beta(latest.index.tolist())

    risk = pd.DataFrame(index=latest.index)

    #Leverage Risk : Debt/EBITDA (higher = need more EBITDA to pay back debt)
    #NetDebt/EBITDA: < 1.0 = safe, > 3.0 = risky
    net_debt_ebitda = latest_ratios["NetDebtToEBITDA"]
    risk["Leverage"] = (net_debt_ebitda / 3.0 * 100).clip(0, 100)

    # Earnings Volatility : Earnings stability (higher = earnings jump around)
    # < 0.02 = very stable, > 0.3 = very volatile
    earnings_growth_vol = ratios_df.groupby("Ticker")["NetIncome_Growth"].std().reindex(risk.index)
    risk["Volatility"] = (earnings_growth_vol / 0.4 * 100).clip(0, 100)

    #Market Risk : Beta (higher = stock moves more than market)
    #Beta: < 1.0 = defensive, > 1.5 = aggressive
    beta = betas.reindex(risk.index)
    risk["Market_Risk"] = ((beta - 0.5) / 1.5 * 100).clip(0, 100)

    #Cash Flow Quality : Earnings → Cash conversion (higher = not converting to cash
    #FCF/NI: > 1.0 = healthy, < 0.5 = risky
    fcf_conversion = latest_ratios["FCF_Conversion"]
    risk["FCF_Quality"] = ((1.5 - fcf_conversion) / 1.5 * 100).clip(0, 100)

    #Composite Score
    risk["Risk_Score"] = risk[["Leverage", "Volatility", "Market_Risk", "FCF_Quality"]].mean(axis=1).round(1)

    score = risk["Risk_Score"] 

    def get_risk_rating(score):
      if score < 25:
            rating = "LOW RISK"
      elif score < 50:
            rating = "MEDIUM RISK"
      else:
            rating = "HIGH RISK"

    risk["Risk_Rating"] = get_risk_rating(score)

    risk["Company"] = risk.index.map(Company)

    result = risk[["Company", "Leverage", "Volatility", "Market_Risk", "FCF_Quality", "Risk_Score","Risk_Rating"]]
    result = result.sort_values("Risk_Score")

    return result
