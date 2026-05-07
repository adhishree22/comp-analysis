
import pandas as pd
from data.config import *
from data.beta_loader import *

def build_risk_scorecard(data_df, ratios_df, year=None):
    
    y = year or data_df["Year"].max()
    latest = data_df[data_df["Year"] == y].set_index("Ticker").copy()
    latest_ratios = ratios_df[ratios_df["Year"] == y].set_index("Ticker").copy()
    
    betas = get_beta(latest.index.tolist())
    
    risk = pd.DataFrame(index=latest.index)
    
    # 1. LEVERAGE RISK (0-100)
    # NetDebt/EBITDA: < 1.0 = safe, > 3.0 = risky
    net_debt_ebitda = latest_ratios["NetDebtToEBITDA"]
    risk["leverage"] = (net_debt_ebitda / 3.0 * 100).clip(0, 100)
    
    # 2. EARNINGS VOLATILITY (0-100)
    # < 0.02 = very stable, > 0.3 = very volatile
    earnings_growth_vol = ratios_df.groupby("Ticker")["NetIncome_Growth"].std().reindex(risk.index)
    risk["volatility"] = (earnings_growth_vol / 0.3 * 100).clip(0, 100)
    
    # 3. MARKET RISK (0-100)
    # Beta: < 1.0 = defensive, > 1.5 = aggressive
    beta = betas.reindex(risk.index)
    risk["market_risk"] = ((beta - 0.5) / 1.5 * 100).clip(0, 100)
    
    # 4. CASH FLOW QUALITY (0-100)
    # FCF/NI: > 1.0 = healthy, < 0.5 = risky
    fcf_conversion = latest_ratios["FCF_Conversion"]
    risk["fcf_quality"] = ((1.5 - fcf_conversion) / 1.5 * 100).clip(0, 100)
    
    # Composite score (average of 4)
    risk["risk_score"] = risk[["leverage", "volatility", "market_risk", "fcf_quality"]].mean(axis=1).round(1)
    
    # Add company names
    risk["company"] = risk.index.map(Company)
    
    # Reorder and sort
    result = risk[["company", "leverage", "volatility", "market_risk", "fcf_quality", "risk_score"]]
    result = result.sort_values("risk_score")
    
    return result
 
 
def scorecard(scorecard):
    """Print risk scorecard nicely"""
    
    print("\n" + "="*80)
    print("RISK SCORECARD (0-100, lower = safer)")
    print("="*80)
    
    print("\n{:<20} {:<12} {:<12} {:<12} {:<12} {:<12}".format(
        "Company", "Leverage", "Volatility", "Market Risk", "FCF Quality", "Risk Score"
    ))
    print("-"*80)
    
    for idx, row in scorecard.iterrows():
        print("{:<20} {:<12.1f} {:<12.1f} {:<12.1f} {:<12.1f} {:<12.1f}".format(
            row["company"],
            row["leverage"],
            row["volatility"],
            row["market_risk"],
            row["fcf_quality"],
            row["risk_score"]
        ))
    
    print("\n" + "="*80)
    print("RISK RATINGS")
    print("="*80)
    
    for idx, row in scorecard.iterrows():
        score = row["risk_score"]
        company = row["company"]
        
        if score < 25:
            rating = "🟢 LOW RISK"
        elif score < 50:
            rating = "🟡 MEDIUM RISK"
        else:
            rating = "🔴 HIGH RISK"
        
        print(f"{company:<25} | {score:5.1f} | {rating}")
    
    print("\n" + "="*80)
    print("WHAT EACH SCORE MEANS")
    print("="*80)
    print("Leverage      : Debt/EBITDA (higher = need more EBITDA to pay back debt)")
    print("Volatility    : Earnings stability (higher = earnings jump around)")
    print("Market Risk   : Beta (higher = stock moves more than market)")
    print("FCF Quality   : Earnings → Cash conversion (higher = not converting to cash)")
    print("\nSafest: Score < 25")
    print("Medium: Score 25-50")
    print("Risky:  Score > 50")
 
