import streamlit as st
import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import plotly.graph_objects as go
import requests
from datetime import timedelta


# Function to fetch adjusted stock prices
def fetch_data(symbols):
    data = {}
    for symbol in symbols:
        stock = yf.Ticker(symbol)
        df = stock.history(period="max")
        if 'Adj Close' in df.columns:
            data[symbol] = df['Adj Close']
        else:
            data[symbol] = df['Close']
    return pd.DataFrame(data)

# calculate daily returns, correlations, and get start/end dates
def calculate_daily_returns(data, days):
    daily_returns = data.pct_change().dropna()
    if days < len(daily_returns):  # Ensure there is enough data
        daily_returns = daily_returns.tail(days)
    correlation_matrix = daily_returns.corr()
    start_date = daily_returns.index.min()
    end_date = daily_returns.index.max()
    return correlation_matrix, start_date, end_date

# Function to calculate average annual return and standard deviation
def calculate_metrics(data):
    annual_returns = {}
    annual_std_devs = {}
    for symbol in data.columns:
        daily_returns = data[symbol].pct_change().dropna()
        annual_return = daily_returns.mean() * 252 * 100  # Annualized return
        annual_std_dev = daily_returns.std() * (252 ** 0.5) * 100  # Annualized std dev
        annual_returns[symbol] = round(annual_return, 2)
        annual_std_devs[symbol] = round(annual_std_dev, 2)
    return annual_returns, annual_std_devs

# plot interactive heatmap with Plotly
def plot_interactive_heatmap(correlation_matrix):
    fig = go.Figure(data=go.Heatmap(
        z=correlation_matrix.values,
        x=correlation_matrix.columns,
        y=correlation_matrix.index,
        colorscale=[[0, 'red'], [0.5, 'yellow'], [1, 'green']],
        zmin=-1,
        zmax=1,
        hoverongaps=False,
        showscale=True,
        text=correlation_matrix.values,
        texttemplate="%{text:.2f}",
        textfont={"size": 12},
        colorbar=dict(title="Correlation", titleside="right")
    ))

    fig.update_layout(
        title='',
        xaxis_title="",
        yaxis_title="",
        xaxis=dict(tickangle=-45),
        yaxis=dict(tickmode="array"),
        autosize=True,
        margin=dict(l=60, r=60, t=50, b=50),
        height=600
    )

    st.plotly_chart(fig)

# Streamlit app with tabs
st.title("Dashboard")

# Create tabs
tab1, tab2 = st.tabs(["Correlation Matrix", "Return & Volatility"])

with tab1:
    st.header("Correlation Matrix")
    st.write("Input stock symbols separated by commas (e.g., SPY, TLT, GLD):")
    symbols_input = st.text_input("Stock Symbols", value="")
    symbols = [symbol.strip().upper() for symbol in symbols_input.split(',')]

    # Add dropdown for selecting time period for correlation calculation
    days_option = st.selectbox(
        "Select period for correlation calculation (in days):",
        options=[5, 10, 21, 63, 126, 252, 504, 756, 1260],
        index=4  # Default to 252 days
    )

    if st.button("Generate"):
        data = fetch_data(symbols)
        if not data.empty:
            correlation_matrix, start_date, end_date = calculate_daily_returns(data, days_option)
            st.write(f"**Correlation Matrix (Based on {days_option}-Day Historical Daily Returns):**")
                     
            plot_interactive_heatmap(correlation_matrix)
        else:
            st.error("No data found for the given symbols. Please check your input.")
            
# annual return & vol tab
with tab2:
    st.header("Annual Return & Volatility")
    st.write("Input stock symbols separated by commas (e.g., SPY, TLT, GLD):")
    symbols_input = st.text_input("Stock Symbols", value="", key="symbols_input_tab2")
    symbols = [symbol.strip().upper() for symbol in symbols_input.split(',')]

    if st.button("Calculate", key="calculate_button_tab2"):
        data = fetch_data(symbols)
        if not data.empty:
            start_date = data.index.min().strftime('%Y-%m-%d')
            end_date = data.index.max().strftime('%Y-%m-%d')
            annual_returns, annual_std_devs = calculate_metrics(data)
            
            st.write("**Average Annual Return & Standard Deviation:**")

            # Display the results
            metrics_df = pd.DataFrame({
                'Annual Return (%)': annual_returns,
                'Annual Standard Deviation (%)': annual_std_devs
            })
            st.dataframe(metrics_df)
        else:
            st.error("No data found for the given symbols. Please check your input.")
