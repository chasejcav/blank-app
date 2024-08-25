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

# Function to calculate daily returns, correlations, and get start/end dates
def calculate_daily_returns(data):
    daily_returns = data.pct_change().dropna()
    start_date = daily_returns.index.min()
    end_date = daily_returns.index.max()
    correlation_matrix = daily_returns.corr()
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


# Function to plot heatmap with custom color scheme
def plot_heatmap(correlation_matrix):
    num_symbols = len(correlation_matrix.columns)
    
    # Define dynamic figure size based on the number of symbols
    fig_width = max(num_symbols, 5) * 1.5
    fig_height = max(num_symbols, 5) * 1.2
    plt.figure(figsize=(fig_width, fig_height))
    
    # Create a custom color map from red (negative), yellow (neutral), to green (positive)
    cmap = LinearSegmentedColormap.from_list(
        'custom_cmap', ['red', 'yellow', 'green'], N=256)

    ax = sns.heatmap(
        correlation_matrix, 
        annot=True, 
        cmap=cmap, 
        vmin=-1, 
        vmax=1,
        center=0,
        linewidths=.5,
        cbar=True,  # Show color bar to indicate scale
        xticklabels=correlation_matrix.columns,
        yticklabels=correlation_matrix.columns,
        annot_kws={"size": max(8, 100 // num_symbols)}  # Adjust text size dynamically
        
    )
    # Create a new axis at the top
    ax.xaxis.set_visible(False)
    ax_top = ax.twiny()
    ax_top.set_xlim(ax.get_xlim())  # Match x-axis limits with the original axis
    
    # Set the ticks to be in the center of each cell
    ax_top.set_xticks([x + 0.5 for x in range(len(correlation_matrix.columns))])
    ax_top.set_xticklabels(correlation_matrix.columns, rotation=0, ha='center')

    # Set label and tick positions
    ax_top.xaxis.set_label_position('top')
    ax_top.xaxis.set_ticks_position('top')

    # Adjust layout for better fitting
    plt.subplots_adjust(top=0.85, bottom=0.15, right=0.85, left=0.15)  # Adjust margins

    st.pyplot(plt.gcf())

# Function to calculate percentage returns over various time periods
def calculate_returns(data):
    time_periods = {
        "1 Day": 1,
        "3 Days": 3,
        "1 Week": 7,
        "2 Weeks": 14,
        "1 Month": 30,
        "3 Months": 90,
        "6 Months": 180,
        "1 Year": 252,
        "2 Years": 504
    }
    
    returns = {}
    for period_name, period_days in time_periods.items():
        returns[period_name] = data.pct_change(periods=period_days).iloc[-1] * 100
    
    return pd.DataFrame(returns)

#  plot the returns heatmap
def plot_returns_heatmap(returns_df):
    # color map (Red for negative, Green for positive)
    cmap = sns.diverging_palette(150, 10, as_cmap=True)  # This creates a palette from green to red

    plt.figure(figsize=(10, 8))
    sns.heatmap(
        returns_df,  # Switch x and y labels
        annot=True, 
        fmt=".2f", 
        cmap=cmap, 
        center=0, 
        linewidths=.5, 
        cbar=False,  # Remove the color bar
        annot_kws={"size": 12}
    )
    plt.title("Returns Heatmap")
    plt.xlabel("Time Period")
    plt.ylabel("Stock Symbol")
    st.pyplot(plt.gcf())

# Streamlit app with tabs
st.title("Dashboard")

# Create tabs
tab1, tab2, tab3 = st.tabs(["Correlation Matrix", "Return & Volatility","Returns Heatmap"])

# corr matrix tab
with tab1:
    st.header("Correlation Matrix")
    st.write("Input stock symbols separated by commas (e.g., SPY, TLT, GLD):")
    symbols_input = st.text_input("Stock Symbols", value="")
    symbols = [symbol.strip().upper() for symbol in symbols_input.split(',')]

    if st.button("Generate Correlation Matrix"):
        data = fetch_data(symbols)
        if not data.empty:
            correlation_matrix, start_date, end_date = calculate_daily_returns(data)
            st.write("**Correlation Matrix (Based on Historical Daily Returns):**")
                     
            plot_heatmap(correlation_matrix)
        else:
            st.error("No data found for the given symbols. Please check your input.")
            
# annual return & vol tab
with tab2:
    st.header("Annual Return & Volatility")
    st.write("Input stock symbols separated by commas (e.g., SPY, TLT, GLD):")
    symbols_input = st.text_input("Stock Symbols", value="", key="symbols_input_tab2")
    symbols = [symbol.strip().upper() for symbol in symbols_input.split(',')]

    if st.button("Calculate Metrics", key="calculate_button_tab2"):
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

    
# Returns Heatmap
with tab3:
    st.header("Returns Heatmap")
    st.write("Input stock symbols separated by commas (e.g., SPY, TLT, GLD):")
    symbols_input = st.text_input("Stock Symbols", value="", key="symbols_input_tab3")
    symbols = [symbol.strip().upper() for symbol in symbols_input.split(',')]

    if st.button("Generate Heatmap", key="heatmap_button_tab3"):
        data = fetch_data(symbols)
        if not data.empty:
            returns_df = calculate_returns(data).T  # Transpose the DataFrame to switch x and y labels
            plot_returns_heatmap(returns_df)
        else:
            st.error("No data found for the given symbols. Please check your input.")
