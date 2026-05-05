
import pandas as pd
from data.config import *

def export_for_tableau(data, ratios):

    fin = data.copy()
    rat = ratios.copy()

    fin["Company"]        = fin["Ticker"].map(Company)
    rat["Company"]        = rat["Ticker"].map(Company)
    fin["Business_Model"] = fin["Ticker"].map(Company_Type)
    rat["Business_Model"] = rat["Ticker"].map(Company_Type)

    fin = fin.sort_values(["Ticker", "Year"]).reset_index(drop=True)
    rat = rat.sort_values(["Ticker", "Year"]).reset_index(drop=True)

    fin.to_csv("dashboard/financials.csv", index=False)
    rat.to_csv("dashboard/ratios.csv",     index=False)

    print(f"financials.csv - {fin.shape}")
    print(f"ratios.csv     - {rat.shape}")

    return fin, rat
