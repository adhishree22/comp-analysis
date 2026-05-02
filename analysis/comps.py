
import pandas as pd
import numpy as np

from src.config import *

def operating_comparison(data, ratios, year=None):
    """
    Covers growth, margins, returns, cash flow quality,
    and leverage. Answers: who runs the better business?
    """
    y   = year or data["Year"].max()
    fin = data[data["Year"] == y].set_index("Ticker")
    rat = ratios[ratios["Year"] == y].set_index("Ticker")

    ops = pd.DataFrame(index=fin.index)

    ops["Revenue"]    = (fin["Revenue"] * Scale).round(1)
    ops["EBITDA"]     = (fin["EBITDA"] * Scale).round(1)
	ops["NetIncome"] = (fin["NetIncome"] * Scale).round(1)
    ops["FCF"]        = (fin["FCF"] * Scale).round(1)

    ops["Rev_Growth"]      = rat["Revenue_Growth"].map("{:.1%}".format)
    ops["NI_Growth"]       = rat["NetIncome_Growth"].map("{:.1%}".format)

    ops["EBITDA Margin"]   = rat["EBITDA_Margin"].map("{:.1%}".format)
    ops["Net Margin"]      = rat["Net_Margin"].map("{:.1%}".format)
    ops["FCF Margin"]      = rat["FCF_Margin"].map("{:.1%}".format)

	ops["ROE"]             = rat["ROE"].map("{:.1%}".format)
    ops["ROA"]             = rat["ROA"].map("{:.1%}".format)

    ops["FCF_Conversion"]       = rat["FCF_Conversion"].map("{:.2f}x".format)

    ops["NetDebtToEBITDA"]       = rat["NetDebtToEBITDA"].map("{:.2f}x".format)
    ops["InterestCoverage"]    = rat["InterestCoverage"].map("{:.1f}x".format)

    ops.index = ops.index.map(Company)
	
    return ops


# ═══════════════════════════════════════════════════
# 2. VALUATION COMPARISON
# How the market prices each business
# ═══════════════════════════════════════════════════
def valuation_comparison(data, ratios, year=None):
    """
    Pure valuation multiples table — the traditional comps.
    Answers: how expensive is each company relative to peers?
    """
    y   = year or data["Year"].max()
    fin = data[data["Year"] == y].set_index("Ticker")
    rat = ratios[ratios["Year"] == y].set_index("Ticker")

    val = pd.DataFrame(index=fin.index)

    val["MarketCap"]  = (fin["MarketCap"]).round(1)
    val["EV"]       = (fin["EV"]).round(1)

    val["EV/EBITDA"]     = rat["EV_EBITDA"].round(1)
    val["EV/Revenue"]    = rat["EV_Revenue"].round(1)
    val["P/E"]           = rat["PE"].round(1)
    val["FCF Yield"]     = rat["FCF_Yield"].map("{:.1%}".format)

    val.index = val.index.map(Company)
    return val


# ═══════════════════════════════════════════════════
# HELPER — Add peer summary rows to any table
# ═══════════════════════════════════════════════════
def add_summary_rows(df, subject="Visa"):

    peers        = df.drop(index=subject, errors="ignore")
    numeric_cols = df.select_dtypes(include="number").columns

    summary = pd.DataFrame({
        "Median": peers[numeric_cols].median().round(1),
        "Mean":   peers[numeric_cols].mean().round(1),
        "High":   peers[numeric_cols].max().round(1),
        "Low":    peers[numeric_cols].min().round(1),
    }).T

    separator = pd.DataFrame(
        [["——"] * len(df.columns)],
        columns=df.columns,
        index=["────────"]
    )

    return pd.concat([df, separator, summary])


# ═══════════════════════════════════════════════════
# 3. IMPLIED VALUATION
# What Visa should be worth using peer multiples
# ═══════════════════════════════════════════════════
def implied_valuation(data, ratios, year=None):

    y     = year or data["Year"].max()
    fin   = data[data["Year"] == y].set_index("Ticker")
    rat   = ratios[ratios["Year"] == y].set_index("Ticker")
    peers = rat.drop(index="V")

    visa_ebitda  = fin.loc["V", "EBITDA"]     
    visa_revenue = fin.loc["V", "Revenue"]    
    visa_ni      = fin.loc["V", "NetIncome"]  
    visa_netdebt = fin.loc["V", "NetDebt"]    
    visa_shares  = fin.loc["V", "Shares"]    
    visa_price   = fin.loc["V", "Close"]      

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

    prices = df["Implied Price"].values
    df["Implied Price"] = df["Implied Price"].map("${:.2f}".format)
    df["vs Current"]    = [
        f"{((p / visa_price) - 1):+.1%}" for p in prices
    ]
    df["Current Price"] = f"${visa_price:.2f}"

    # ── Price range summary row ───────────────────
    range_row = pd.DataFrame([{
        "Peer Median":   "——",
        "Peer Mean":     "——",
        "Implied Price": f"${min(prices):.2f} – ${max(prices):.2f}",
        "vs Current":    f"Current: ${visa_price:.2f}",
        "Current Price": "——",
    }], index=["── Range ──"])

    return pd.concat([df, range_row])
