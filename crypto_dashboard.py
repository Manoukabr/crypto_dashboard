import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

st.title("Crypto Dashboard – Analyse Bitcoin")

# --- Choix de la crypto et de la devise ---
crypto = "bitcoin"  # Dashboard ciblé sur Bitcoin
devise = st.selectbox("Choisissez la devise", ["usd", "eur"])

# --- Récupération des données historiques 90 derniers jours ---
url_history = f"https://api.coingecko.com/api/v3/coins/{crypto}/market_chart?vs_currency={devise}&days=90"
response_history = requests.get(url_history).json()
prices = response_history['prices']

dates = [datetime.fromtimestamp(p[0]/1000) for p in prices]
prix = [p[1] for p in prices]
df = pd.DataFrame({"Date": dates, "Prix": prix})

# --- Calcul des indicateurs financiers ---
df['SMA_10'] = df['Prix'].rolling(window=10).mean()
df['EMA_10'] = df['Prix'].ewm(span=10, adjust=False).mean()

# RSI
delta = df['Prix'].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)
avg_gain = gain.rolling(14).mean()
avg_loss = loss.rolling(14).mean()
rs = avg_gain / avg_loss
df['RSI'] = 100 - (100 / (1 + rs))

# MACD
ema_12 = df['Prix'].ewm(span=12, adjust=False).mean()
ema_26 = df['Prix'].ewm(span=26, adjust=False).mean()
df['MACD'] = ema_12 - ema_26
df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

# Bollinger Bands
df['BB_Mid'] = df['Prix'].rolling(window=20).mean()
df['BB_Upper'] = df['BB_Mid'] + 2*df['Prix'].rolling(window=20).std()
df['BB_Lower'] = df['BB_Mid'] - 2*df['Prix'].rolling(window=20).std()

# --- Sélection des indicateurs à afficher ---
st.sidebar.header("Indicateurs")
show_sma = st.sidebar.checkbox("SMA 10", True)
show_ema = st.sidebar.checkbox("EMA 10", True)
show_rsi = st.sidebar.checkbox("RSI", False)
show_macd = st.sidebar.checkbox("MACD", False)
show_bb = st.sidebar.checkbox("Bollinger Bands", False)

# --- Création du graphique principal ---
fig = go.Figure()
fig.add_trace(go.Scatter(x=df['Date'], y=df['Prix'], mode='lines', name='Prix'))

if show_sma:
    fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA_10'], mode='lines', name='SMA 10'))
if show_ema:
    fig.add_trace(go.Scatter(x=df['Date'], y=df['EMA_10'], mode='lines', name='EMA 10'))
if show_bb:
    fig.add_trace(go.Scatter(x=df['Date'], y=df['BB_Upper'], mode='lines', name='BB Upper', line=dict(dash='dash')))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['BB_Lower'], mode='lines', name='BB Lower', line=dict(dash='dash')))

fig.update_layout(title=f"Analyse technique du Bitcoin en {devise.upper()}",
                  xaxis_title="Date", yaxis_title=f"Prix ({devise.upper()})")

st.plotly_chart(fig, use_container_width=True)

# --- Graphiques secondaires pour RSI et MACD ---
if show_rsi:
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=df['Date'], y=df['RSI'], mode='lines', name='RSI'))
    fig_rsi.update_layout(title="RSI", yaxis=dict(range=[0,100]))
    st.plotly_chart(fig_rsi, use_container_width=True)

if show_macd:
    fig_macd = go.Figure()
    fig_macd.add_trace(go.Scatter(x=df['Date'], y=df['MACD'], mode='lines', name='MACD'))
    fig_macd.add_trace(go.Scatter(x=df['Date'], y=df['Signal'], mode='lines', name='Signal'))
    fig_macd.update_layout(title="MACD")
    st.plotly_chart(fig_macd, use_container_width=True)
