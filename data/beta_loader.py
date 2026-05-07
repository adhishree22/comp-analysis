
import yfinance as yf
import pandas as pd

def get_beta(tickers):

    betas = {}
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            beta = stock.info.get('beta', 1.0)
            betas[ticker] = beta if beta else 1.0
        except:
            betas[ticker] = 1.0

    beta = pd.Series(betas)
    
    return beta
