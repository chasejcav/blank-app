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

# Function to calculate portfolio metrics
def calculate_portfolio_metrics(daily_returns, weights):
    portfolio_returns = daily_returns.dot(weights)
    annual_return = portfolio_returns.mean() * 252 * 100
    annual_std_dev = portfolio_returns.std() * (252 ** 0.5) * 100
    return round(annual_return, 2), round(annual_std_dev, 2)

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
    st.header("Return & Volatility")
    symbols_input = st.text_input("Stock Symbols (comma-separated)", value="", key="tab2_symbols")
    weights_input = st.text_input("Weights (comma-separated)", value="", key="tab2_weights")
    symbols = [symbol.strip().upper() for symbol in symbols_input.split(',')]
    
    # Validate weights input
    try:
        weights = [float(weight.strip()) for weight in weights_input.split(',') if weight.strip() != ""]
    except ValueError:
        st.error("Error: All weights must be numeric values.")
        weights = []
    
    if st.button("Calculate Portfolio Metrics"):
        if len(weights) != len(symbols):
            st.error("Error: The number of weights does not match the number of tickers.")
        else:
            data = fetch_data(symbols)
            if not data.empty:
                daily_returns, start_date, end_date = calculate_daily_returns(data)
                annual_return, annual_std_dev = calculate_portfolio_metrics(daily_returns, weights)
                
                st.write(f"**Data used from {start_date.date()} to {end_date.date()}**")
                st.write(f"**Annual Return (%):** {annual_return}")
                st.write(f"**Annual Standard Deviation (%):** {annual_std_dev}")
            else:
                st.error("No data found for the given symbols. Please check your input.")
