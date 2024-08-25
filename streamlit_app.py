import streamlit as st
import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import plotly.graph_objects as go
import requests


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

# Define your FRED API key and base URL
FRED_API_KEY = '25e2b0598c9846c50064eb3a0d2a30b7'

# Function to fetch yield curve data from FRED API
def fetch_yield_curve():
    # Example series IDs for U.S. Treasury yields (you may need to adjust these)
    series_ids = {
        '1M': 'DTB1YR',  # 1-month Treasury
        '3M': 'DTB3',    # 3-month Treasury
        '6M': 'DTB6',    # 6-month Treasury
        '1Y': 'DTB1',    # 1-year Treasury
        '2Y': 'GS2',     # 2-year Treasury
        '5Y': 'GS5',     # 5-year Treasury
        '10Y': 'GS10',   # 10-year Treasury
        '30Y': 'GS30'    # 30-year Treasury
    }
    
    # Fetch data for all series
    yield_data = {}
    for maturity, series_id in series_ids.items():
        url = f"https://fred.stlouisfed.org/data/{series_id}&api_key={FRED_API_KEY}&file_type=csv"
        df = pd.read_csv(url, parse_dates=['DATE'], index_col='DATE')
        yield_data[maturity] = df[series_id]
    
    # Combine all series into a single DataFrame
    yield_df = pd.DataFrame(yield_data)
    return yield_df

# Function to plot yield curve using plotly
def plot_yield_curve(df):
    fig = go.Figure()
    
    # Add traces for each maturity
    for column in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[column],
            mode='lines+markers',
            name=f'{column} Yield Curve',
            line=dict(width=2)
        ))
    
    fig.update_layout(
        title='Current Yield Curve',
        xaxis_title='Date',
        yaxis_title='Yield (%)',
        xaxis=dict(type='date'),
        template='plotly_white'
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

    if st.button("Generate Correlation Matrix"):
        data = fetch_data(symbols)
        if not data.empty:
            correlation_matrix, start_date, end_date = calculate_daily_returns(data)
            st.write(f"**Data used from {start_date.date()} to {end_date.date()}**")
            st.write("**Correlation Matrix (Based on Daily Returns):**")
                     
            plot_heatmap(correlation_matrix)
        else:
            st.error("No data found for the given symbols. Please check your input.")


with tab2:
    st.header("Yield Curve")
    
    # Fetch and plot the yield curve data
    yield_curve_df = fetch_yield_curve()
    if not yield_curve_df.empty:
        plot_yield_curve(yield_curve_df)
    else:
        st.error("Failed to fetch yield curve data.")
   
