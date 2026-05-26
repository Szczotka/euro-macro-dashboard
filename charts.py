import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

# Brand colors for each index (national/institutional colors)
COLORS = {
    "CAC40": "#003189",        # French blue
    "DAX": "#000000",          # German black
    "FTSE100": "#C8102E",      # British red
    "EuroStoxx50": "#F7D117",  # EU yellow
    "ECB Rate": "#FF6B00",     # Orange
    "inflation": "#00A86B"     # Green
}


def plot_indices(close):
    """
    Normalized performance chart of European indices.
    All indices rebased to 100 at the start of the period
    for direct comparison regardless of absolute price levels.
    """
    # Rebase to 100 using first valid value per index
    first_valid = close.apply(lambda col: col.dropna().iloc[0])
    normalized = (close / first_valid) * 100

    fig = go.Figure()
    for col in normalized.columns:
        fig.add_trace(go.Scatter(
            x=normalized.index,
            y=normalized[col],
            name=col,
            line=dict(color=COLORS[col], width=2)
        ))

    fig.update_layout(
        title="European Indices Performance (base 100)",
        xaxis_title="Date",
        yaxis_title="Performance (base 100)",
        hovermode="x unified",
        legend=dict(orientation="h", y=-0.2)
    )
    return fig


def plot_macro(ecb_rate, inflation):
    """
    Dual-axis chart comparing ECB deposit facility rate
    against Euro area HICP inflation.
    Allows visual analysis of monetary policy response to inflation.
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Resample ECB rate to monthly for visual clarity
    ecb_monthly = ecb_rate.resample("ME").last()

    fig.add_trace(go.Scatter(
        x=ecb_monthly.index,
        y=ecb_monthly.values,
        name="ECB Rate (%)",
        line=dict(color=COLORS["ECB Rate"], width=2)
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=inflation.index,
        y=inflation["inflation"],
        name="Inflation HICP (%)",
        line=dict(color=COLORS["inflation"], width=2, dash="dot")
    ), secondary_y=True)

    fig.update_layout(
        title="ECB Interest Rate vs Euro Area Inflation",
        hovermode="x unified",
        legend=dict(orientation="h", y=-0.2)
    )
    fig.update_yaxes(title_text="ECB Rate (%)", secondary_y=False)
    fig.update_yaxes(title_text="Inflation (%)", secondary_y=True)
    return fig


def plot_correlation(close, ecb_rate):
    """
    Correlation heatmap between monthly index returns
    and ECB rate changes over the selected period.
    Note: ECB rate changes are infrequent — longer periods yield richer results.
    """
    # Monthly returns for indices (in %)
    monthly = close.resample("ME").last().pct_change().dropna() * 100

    # Monthly ECB rate changes
    ecb_monthly = ecb_rate.resample("ME").last().diff().dropna()
    ecb_monthly.name = "ECB Rate Change"

    # Merge on common dates
    merged = pd.concat([monthly, ecb_monthly], axis=1).dropna()
    corr = merged.corr().round(2)

    fig = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="RdBu",
        zmin=-1, zmax=1,
        title="Correlation Matrix: Indices Returns vs ECB Rate Changes"
    )
    return fig