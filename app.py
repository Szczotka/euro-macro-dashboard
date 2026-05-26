import streamlit as st
from data import get_indices, get_ecb_rate, get_inflation
from charts import plot_indices, plot_macro, plot_correlation

# Page configuration 
st.set_page_config(
    page_title="Euro Macro Dashboard",
    page_icon="🇪🇺",
    layout="wide"
)

# Header 
st.title("🇪🇺 Euro Macro Dashboard")
st.markdown("*Tracking European markets alongside ECB monetary policy*")
st.divider()

# Sidebar
st.sidebar.title("⚙️ Settings")
st.sidebar.markdown("---")
period = st.sidebar.selectbox(
    "Time period",
    options=["6mo", "1y", "2y"],
    index=2
)

# Map period to start date for macro data
start_date_map = {
    "6mo": "2024-11-01",
    "1y":  "2024-01-01",
    "2y":  "2023-01-01"
}
start_date = start_date_map[period]

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **Data sources**
    - 📈 [Yahoo Finance](https://finance.yahoo.com) — Indices
    - 🏦 [FRED](https://fred.stlouisfed.org) — ECB Rate
    - 🇪🇺 [Eurostat](https://ec.europa.eu/eurostat) — Inflation
    """
)

# Data loading 
@st.cache_data(ttl=3600)
def load_data(period, start_date):
    """Load all data sources. Cached for 1 hour."""
    close = get_indices(period)
    ecb_rate = get_ecb_rate(start_date)
    inflation = get_inflation(start_date)
    return close, ecb_rate, inflation

with st.spinner("Loading market data..."):
    close, ecb_rate, inflation = load_data(period, start_date)

# KPI row 
col1, col2, col3, col4, col5, col6 = st.columns(6)

# Use last valid value to avoid NaN on market holidays
latest = close.apply(lambda col: col.dropna().iloc[-1])
prev = close.apply(lambda col: col[col != col.iloc[-1]].dropna().iloc[-1])

col1.metric("CAC40",       f"{latest['CAC40']:.0f}",       f"{((latest['CAC40']/prev['CAC40'])-1)*100:.2f}%")
col2.metric("DAX",         f"{latest['DAX']:.0f}",         f"{((latest['DAX']/prev['DAX'])-1)*100:.2f}%")
col3.metric("FTSE100",     f"{latest['FTSE100']:.0f}",     f"{((latest['FTSE100']/prev['FTSE100'])-1)*100:.2f}%")
col4.metric("EuroStoxx50", f"{latest['EuroStoxx50']:.0f}", f"{((latest['EuroStoxx50']/prev['EuroStoxx50'])-1)*100:.2f}%")
col5.metric("ECB Rate",    f"{ecb_rate.iloc[-1]:.2f}%")
col6.metric("Inflation",   f"{inflation['inflation'].iloc[-1]:.1f}%")

st.divider()

# Tabs
tab1, tab2, tab3 = st.tabs(["📈 Markets", "🏦 Macro", "🔗 Correlation"])

with tab1:
    st.plotly_chart(plot_indices(close), use_container_width=True)

with tab2:
    st.plotly_chart(plot_macro(ecb_rate, inflation), use_container_width=True)

with tab3:
    st.plotly_chart(plot_correlation(close, ecb_rate), use_container_width=True)
    st.caption("⚠️ ECB rate changes are infrequent. Select a longer period for meaningful correlation data.")

# Footer
st.divider()
st.caption("Data refreshed every hour · Yahoo Finance · FRED (Federal Reserve) · Eurostat")