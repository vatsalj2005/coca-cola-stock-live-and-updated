# coca_cola_dashboard.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import yfinance as yf
import numpy as np

# Load model
model = joblib.load("coca_rf_model.pkl")
features = ['Open', 'High', 'Low', 'Close', 'Volume', 'MA20', 'MA50', 'Volatility', 'Daily Return']

# Load stock history
stock_df = pd.read_csv("Coca-Cola_stock_history.csv")
stock_df['Date'] = pd.to_datetime(stock_df['Date'], errors='coerce', utc=True).dt.tz_convert(None)
stock_df.dropna(subset=['Date'], inplace=True)
stock_df.sort_values('Date', inplace=True)

# Feature engineering
stock_df['MA20'] = stock_df['Close'].rolling(window=20).mean()
stock_df['MA50'] = stock_df['Close'].rolling(window=50).mean()
stock_df['Daily Return'] = stock_df['Close'].pct_change()
stock_df['Volatility'] = stock_df['Close'].rolling(window=20).std()
stock_df.dropna(inplace=True)

# === Streamlit UI ===
st.title("📊 Coca-Cola Stock Analysis & Live Prediction")

tab1, tab2 = st.tabs(["📈 Historical Analysis", "🔮 Live Prediction"])

with tab1:
    st.subheader("Stock Price with Moving Averages")
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(stock_df['Date'], stock_df['Close'], label='Close Price')
    ax.plot(stock_df['Date'], stock_df['MA20'], label='MA20')
    ax.plot(stock_df['Date'], stock_df['MA50'], label='MA50')
    ax.set_xlabel("Date"); ax.set_ylabel("Price")
    ax.legend(); ax.grid()
    st.pyplot(fig)

    st.subheader("Volume Traded Over Time")
    fig2, ax2 = plt.subplots(figsize=(12, 4))
    ax2.plot(stock_df['Date'], stock_df['Volume'], color='purple')
    st.pyplot(fig2)

    st.subheader("Dividend History")
    fig3, ax3 = plt.subplots(figsize=(12, 4))
    ax3.plot(stock_df['Date'], stock_df['Dividends'], color='green')
    st.pyplot(fig3)

    st.subheader("Daily Return Distribution")
    fig4, ax4 = plt.subplots(figsize=(8, 4))
    sns.histplot(stock_df['Daily Return'], bins=100, kde=True, color='orange', ax=ax4)
    st.pyplot(fig4)

with tab2:
    st.subheader("Live Prediction Using Yahoo Finance")
    live_df = yf.download('KO', period='3mo', interval='1d')
    live_df.dropna(inplace=True)

    # Flatten the multi-level column names
    live_df.columns = [col if isinstance(col, str) else col[0] for col in live_df.columns]

    # Feature engineering
    live_df['MA20'] = live_df['Close'].rolling(window=20).mean()
    live_df['MA50'] = live_df['Close'].rolling(window=50).mean()
    live_df['Daily Return'] = live_df['Close'].pct_change()
    live_df['Volatility'] = live_df['Close'].rolling(window=20).std()
    live_df.dropna(inplace=True)

    # Prepare features
    latest = live_df.iloc[-1][features].values.reshape(1, -1)
    prediction = model.predict(latest)[0]

    st.metric("Tomorrow's Prediction", "📈 UP" if prediction == 1 else "📉 DOWN")
    st.dataframe(live_df.tail(3)[features])