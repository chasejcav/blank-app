# app.py

import streamlit as st
import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

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
    plt.figure(figsize=(10, 6))
    
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
        
    )
    # Hide default x-axis labels and ticks
    ax.set_xticks([])
    ax.set_xticklabels([])

    # Add x-axis labels to the top
    ax_top = ax.twiny()
    ax_top.set_xlim(ax.get_xlim())  # Set the limits to match the original axis
    ax_top.set_xticks(range(len(correlation_matrix.columns)))
    ax_top.set_xticklabels(correlation_matrix.columns, rotation=90)
    ax_top.set_xlabel('Stock Symbols')

    # Adjust layout to fit the plot
    plt.tight_layout()

    st.pyplot(plt.gcf())

# Streamlit app
st.title("Stock Correlation Matrix")

st.write("Input stock symbols separated by commas (e.g., SPY, TLT, GLD):")
symbols_input = st.text_input("Stock Symbols", value="")
symbols = [symbol.strip().upper() for symbol in symbols_input.split(',')]

if st.button("Generate Correlation Matrix"):
    data = fetch_data(symbols)
    if not data.empty:
        # Calculate daily returns and correlation matrix
        correlation_matrix, start_date, end_date = calculate_daily_returns(data)

        # Display the start and end date
        st.write(f"Data used from {start_date.date()} to {end_date.date()}")

        # Display the heatmap
        st.write("Correlation Matrix Heatmap (Based on Daily Returns):")
        plot_heatmap(correlation_matrix)
    else:
        st.write("Failed to fetch data for the symbols provided.")


