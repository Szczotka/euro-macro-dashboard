import os
import yfinance as yf
import pandas as pd
import eurostat
from fredapi import Fred
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
FRED_API_KEY = os.getenv("FRED_API_KEY")

# European indices with their Yahoo Finance tickers
INDICES = {
    "CAC40": "^FCHI",        # France
    "DAX": "^GDAXI",         # Germany
    "FTSE100": "^FTSE",      # United Kingdom
    "EuroStoxx50": "^STOXX50E"  # Eurozone broad index
}


def get_indices(period="2y"):
    """
    Download daily closing prices for European indices.
    Missing values (public holidays) are forward-filled.
    """
    data = yf.download(
        tickers=list(INDICES.values()),
        period=period,
        interval="1d",
        auto_adjust=True,
        progress=False
    )
    close = data["Close"]
    # Rename columns from Yahoo tickers to readable names
    ticker_to_name = {v: k for k, v in INDICES.items()}
    close = close.rename(columns=ticker_to_name)
    close.columns.name = None
    # Forward-fill missing values caused by different market holidays
    close = close.ffill()
    return close


def get_ecb_rate(start_date="2024-01-01"):
    """
    Fetch ECB deposit facility rate from FRED.
    Source: Federal Reserve Economic Data (FRED), series ECBDFR.
    """
    fred = Fred(api_key=FRED_API_KEY)
    rate = fred.get_series("ECBDFR", observation_start=start_date)
    rate.name = "ECB Rate"
    return rate


def get_inflation(start_date="2024-01-01"):
    """
    Fetch Euro area HICP inflation (annual rate of change)
    for all items, from Eurostat official API.
    Geography: EA20 (Euro area - 20 countries).
    """
    hicp = eurostat.get_data_df("prc_hicp_manr")
    hicp_ea = hicp[
        (hicp["geo\\TIME_PERIOD"] == "EA20") &
        (hicp["coicop"] == "AP") &       # AP = All products
        (hicp["unit"] == "RCH_A")        # RCH_A = Annual rate of change
    ].copy()
    # Reshape: keep only date columns and transpose
    date_cols = [col for col in hicp_ea.columns if col.startswith("20")]
    hicp_ea = hicp_ea[date_cols].T
    hicp_ea.columns = ["inflation"]
    hicp_ea.index = pd.to_datetime(hicp_ea.index)
    hicp_ea = hicp_ea[start_date:]
    return hicp_ea