
import pandas as pd
from data.config import *

def export_for_tableau(data, ratios):

    fin = data.copy()
    rat = ratios.copy()

    # Add full company name for Tableau labels
    fin.insert(0, "Company", fin["Ticker"].map(Company))
    rat.insert(0, "Company", rat["Ticker"].map(Company))

    fin.insert(1, "Business Model", fin["Ticker"].map(Company_Type))
    rat.insert(1, "Business Model", rat["Ticker"].map(Company_Type))

    fin = fin.sort_values(["Ticker", "Year"]).reset_index(drop=True)
    rat = rat.sort_values(["Ticker", "Year"]).reset_index(drop=True)

    fin.to_csv("/content/comp-analysis/dashboard/financials.csv", index=False)
    rat.to_csv("/content/comp-analysis/dashboard/ratios.csv", index=False)

    print(f"financials.csv - {fin.shape}")
    print(f"ratios.csv - {rat.shape}")

    return fin, rat
