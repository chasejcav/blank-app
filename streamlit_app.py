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

# Streamlit app with tabs
st.title("Stock Analysis Dashboard")

# Create tabs
tab1, tab2, tab3 = st.tabs(["Instructions", "Correlation Matrix", "Portfolio Return & Volatility"])

with tab2:
    st.header("Correlation Matrix")
    st.write("Input stock symbols separated by commas (e.g., SPY, TLT, GLD):")
    symbols_input = st.text_input("Stock Symbols", value="")
    symbols = [symbol.strip().upper() for symbol in symbols_input.split(',')]

    if st.button("Generate Correlation Matrix"):
        data = fetch_data(symbols)
        if not data.empty:
            correlation_matrix, start_date, end_date = calculate_daily_returns(data)
            st.write(f"Data used from {start_date.date()} to {end_date.date()}")
            st.write("Correlation Matrix Heatmap (Based on Daily Returns):")
            plot_heatmap(correlation_matrix)
        else:
            st.error("No data found for the given symbols. Please check your input.")

with tab1:
    st.header("Instructions")
    st.write("""
        1. **Input Stock Symbols**: Enter the stock symbols separated by commas (e.g., SPY, TLT, GLD) in the text box.
        2. **Generate Correlation Matrix**: Click the button to generate and view the correlation matrix based on daily returns.
        3. **Data Range**: The displayed data range will show the start and end dates of the available data for the selected stocks.
    """)

with tab3:
    st.header("Portfolio Metrics")
    st.write("Input stock symbols separated by commas (e.g., SPY, TLT, GLD):")
    symbols_input = st.text_input("Stock Symbols (for Portfolio Metrics)", value="")
    symbols = [symbol.strip().upper() for symbol in symbols_input.split(',')]

    if symbols:
        weights_input = st.text_input("Enter Weights (comma-separated, e.g., 0.4, 0.4, 0.2)", value="")
        try:
            weights = [float(w) for w in weights_input.split(',') if w.strip()]
        except ValueError:
            st.error("Invalid weight values. Please ensure all weights are numeric and properly formatted.")
            weights = []

        if len(symbols) == len(weights):
            data = fetch_data(symbols)
            if not data.empty:
                daily_returns, _, _, _ = calculate_daily_returns(data)
                annual_return, annual_std_dev = calculate_portfolio_metrics(daily_returns, weights)
                st.write(f"Annual Average Return: {annual_return:.2%}")
                st.write(f"Annual Standard Deviation: {annual_std_dev:.2%}")
            else:
                st.error("No data found for the given symbols. Please check your input.")
        else:
            st.error("The number of weights must match the number of stock symbols.")
