import streamlit as st
import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

@st.cache_data
def fetch_data(symbols):
    data = {}
    for symbol in symbols:
        stock = yf.Ticker(symbol)
        df = stock.history(period="1y")  # Limiting to the past year for faster loading
        if 'Adj Close' in df.columns:
            data[symbol] = df['Adj Close']
        else:
            data[symbol] = df['Close']
    return pd.DataFrame(data)

@st.cache_data
def calculate_daily_returns(data):
    daily_returns = data.pct_change().dropna()
    start_date = daily_returns.index.min()
    end_date = daily_returns.index.max()
    correlation_matrix = daily_returns.corr()
    return correlation_matrix, start_date, end_date

def plot_heatmap(correlation_matrix):
    plt.figure(figsize=(10, 6))
    
    cmap = LinearSegmentedColormap.from_list(
        'custom_cmap', ['red', 'yellow', 'green'], N=256)

    sns.heatmap(
        correlation_matrix, 
        annot=True, 
        cmap=cmap, 
        vmin=-1, 
        vmax=1,
        center=0,
        linewidths=.5,
        cbar=True,  
        xticklabels=correlation_matrix.columns,
        yticklabels=correlation_matrix.columns
    )
    
    st.pyplot(plt.gcf())

st.title("Stock Correlation Matrix")

st.write("Input stock symbols separated by commas (e.g., AAPL, MSFT, GOOGL):")
symbols_input = st.text_input("Stock Symbols", value="SPY,TLT,GLD")
symbols = [symbol.strip().upper() for symbol in symbols_input.split(',')]

if st.button("Generate Correlation Matrix"):
    data = fetch_data(symbols)
    if not data.empty:
        correlation_matrix, start_date, end_date = calculate_daily_returns(data)
        st.write(f"Data used from {start_date.date()} to {end_date.date()}")
        st.write("Correlation Matrix Heatmap (Based on Daily Returns):")
        plot_heatmap(correlation_matrix)
    else:
        st.write("Failed to fetch data for the symbols provided.")

