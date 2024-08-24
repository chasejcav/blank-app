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
    # Create a new axis at the top
    ax_top = ax.twiny()
    ax_top.set_xlim(ax.get_xlim())  # Match x-axis limits with the original axis
    
    # Set the ticks to be in the center of each cell
    ax_top.set_xticks([x + 0.5 for x in range(len(correlation_matrix.columns))])
    ax_top.set_xticklabels(correlation_matrix.columns, rotation=90, ha='center')

    # Set label and tick positions
    ax_top.xaxis.set_label_position('top')
    ax_top.xaxis.set_ticks_position('top')

    # Adjust layout for better fitting
    plt.subplots_adjust(top=0.85, bottom=0.15, right=0.85, left=0.15)  # Adjust margins

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


