# Payments Industry — Comparable Company Analysis

A full-stack comp analysis project analyzing **Visa, Mastercard, American Express, and PayPal** across financial performance, profitability, cash flow, valuation, and growth dimensions.

Built end-to-end with a modular Python pipeline for data ingestion, ratio analysis, EDA, comps, and risk scoring — with Tableau for interactive buy-side style visualization.

---

## Live Dashboard

https://public.tableau.com/views/CompAnalysis_17780395604670/PaymentsIndustryCompAnalysis?:language=en-US&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link

---

## Project Structure

```
├── data/
│   ├── beta_loader.py           # yfinance fetching beta data
│   ├── config.py                # Tickers, scale, and constants
│   ├── data_loader.py           # yfinance fetching and financial dataframe construction
│   ├── export_tableau.py        # Exports clean CSVs for Tableau
│   ├── pipeline.py              # Orchestrates full dataset build
│   └── price_loader.py         # yfinance fetching and price data construction
│
├── analysis/
│   ├── ratio_analysis.py        # Computes 27+ financial ratios
│   ├── eda.py                   # EDA — growth, margin, cashflow, leverage, valuation, correlation, outliers
│   ├── comps.py                 # Operating comparison, valuation comparison, implied valuation
│   └── risk_score.py            # Composite risk scorecard
│
├── dashboard/                   # CSVs and Tableau Workbook
│
├── Comps_Analysis.ipynb         # Main orchestration notebook
└── README.md
```

---

## How It Works

```python
# 1. Build financial dataset from yfinance
from data.pipeline import *
data_df = build_dataset()

# 2. Compute 27+ ratios
from analysis.ratio_analysis import *
ratios_df = add_ratios(data_df)

# 3. Exploratory Data Analysis
from analysis.eda import *
growth_analysis(data_df, ratios_df)
margin_analysis(ratios_df)
cashflow_analysis(ratios_df)
leverage_analysis(ratios_df)
valuation_analysis(ratios_df)
correlation_heatmap(ratios_df)
flag_outliers(data_df, ratios_df)

# 4. Comparable Company Analysis
from analysis.comps import *
operating_comparison(data_df, ratios_df)   # How businesses perform
valuation_comparison(data_df, ratios_df)   # How market prices each business
implied_valuation(data_df, ratios_df)      # What Visa should be worth using peer multiples

# 5. Risk Scorecard
from analysis.risk_score import *
build_risk_scorecard(data_df, ratios_df)

# 6. Export for Tableau
from data.export_tableau import *
export_for_tableau(data_df, ratios_df)
```

---

## Data Sources

- **yfinance** — income statement, balance sheet, cash flow statement (FY2022–FY2025) , historical price data , beta
- Tickers: **V, MA, AXP, PYPL**

---

## Key Metrics Covered

**Financials**
Revenue, Net Income, EBIT, EBITDA, OCF, CapEx, FCF, EPS, Shares, Market Cap, Net Debt, Enterprise Value, Total Assets, Equity, Total Debt, Cash, Depreciation, Interest, Tax, Beta, Closing Price

**Ratios**
Net Margin, Operating Margin, EBITDA Margin, FCF Margin, ROE, ROA, Debt/Equity, Debt/EBITDA, Net Debt/EBITDA, Interest Coverage, FCF Conversion, OCF/Net Income, FCF/EBITDA, FCF Yield, P/E, EV/EBITDA, EV/Revenue, Earnings Volatility

**Growth**
Revenue Growth, Net Income Growth, EBITDA Growth, EBIT Growth, FCF Growth (all YoY)

---

## Analysis Modules

**EDA (`analysis/eda.py`)**
Six dedicated analysis functions covering growth, margins, cash flow quality, leverage, and valuation multiples. Also includes a correlation heatmap across all 27+ ratios and automated outlier flagging.

**Comps (`analysis/comps.py`)**
- Operating comparison — benchmarks each company on fundamentals
- Valuation comparison — how the market prices each business relative to peers
- Implied valuation — derives what Visa should be worth using peer median and mean multiples (P/E, EV/EBITDA, EV/Revenue), with upside/(downside) vs current price

**Risk Scorecard (`analysis/risk_score.py`)**
Composite risk score built from leverage, interest coverage, earnings volatility, and FCF quality — produces a company-level risk ranking.

**Tableau Export (`data/export_tableau.py`)**
Exports two clean CSVs — financials and ratios — formatted for direct use as Tableau data sources.

---

## Tableau Story — 6 Dashboards

| # | Dashboard | Key Charts |
|---|-----------|------------|
| 1 | **Executive Overview** | KPI cards (Revenue, NI, Market Cap), Revenue/EBITDA/FCF trends |
| 2 | **Margin Analysis** | Margin trends over time, margin comparison across all 4 margin types |
| 3 | **Profitability & Returns** | Revenue-to-NI bridge, ROE trend, ROA trend, ROA vs ROE comparison |
| 4 | **Cash Flow & Capital Efficiency** | FCF conversion, FCF yield, Net Debt/EBITDA, interest coverage, debt/equity trend |
| 5 | **Valuation & Risk** | Valuation multiples snapshot, P/E trend, EV/EBITDA, EV/Revenue, earnings volatility |
| 6 | **Growth Analysis** | YoY growth comparison, revenue/EBITDA/NI/FCF growth trends |

---

## Key Findings

**Executive Overview**
- Visa leads on market cap ($657B) and FCF ($21.58B) with $40B revenue in FY2025
- Mastercard generates the strongest net income relative to revenue at $14.97B on $32.79B
- PayPal lags significantly on market cap ($54B) despite $33.17B in revenue

**Margin Analysis**
- Visa operates at 66.4% operating margin and 53.9% FCF margin — pure network economics
- PayPal's 19.3% operating margin signals structural pressure vs pure network peers
- Mastercard's margins are stable and expanding across all four margin types

**Profitability & Returns**
- Mastercard's ROE of 193.5% reflects extreme capital efficiency in an asset-light model
- Wide ROA-ROE spread across all companies reveals leverage as a key return amplifier
- PayPal's ROE of 25.8% is respectable but driven by fundamentally different economics

**Cash Flow & Capital Efficiency**
- PayPal has the highest FCF yield at 10% — cheapest on cash relative to market cap
- American Express carries the highest Net Debt/EBITDA at 0.65x
- Visa's interest coverage of 45x makes it the most financially resilient in the group

**Valuation & Risk**
- Mastercard trades at 33.98x P/E and 25.29x EV/EBITDA — a clear quality premium
- PayPal at 10.23x P/E looks cheap but earnings volatility of 0.39 vs Mastercard's 0.02 explains the discount
- Implied valuation analysis suggests Visa trades at a 29–35% premium to peer median multiples, reflecting its network moat

**Growth Analysis**
- Mastercard leads with 31.83% NI growth in FY2025
- PayPal's FCF growth of -17.78% raises durability concerns despite revenue resilience
- Visa maintains steady double-digit revenue growth at 11.34%

---

## Tools & Technologies

| Tool | Usage |
|------|-------|
| Python (Pandas, NumPy) | Data engineering, ratio calculation, EDA, comps, risk scoring |
| yfinance | Financial statement data retrieval |
| Modular Python scripts | Clean separation across pipeline, ratios, EDA, comps, risk, export |
| Tableau Public | Interactive 6-dashboard story with global filters |

---

## How to Run

```bash
# Clone the repo
git clone https://github.com/Adhishree22/Comp_Analysis.git
cd Comp_Analysis

# Install dependencies
pip install pandas numpy yfinance

# Run the model
notebook Comps_Analysis.ipynb
```

---
