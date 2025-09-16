import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

st.title("Dashboard Valeur de Monnaie")

# Choix de la crypto et devise
crypto = st.selectbox("Choisissez une crypto", ["bitcoin", "ethereum", "dogecoin"])
devise = st.selectbox("Choisissez la devise", ["usd", "eur"])

# Récupération du prix actuel
url_current = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies={devise}"
response_current = requests.get(url_current).json()
valeur = response_current[crypto][devise]
st.metric(label=f"Prix actuel de {crypto} en {devise.upper()}", value=valeur)

# Récupération de l'historique sur 30 jours
url_history = f"https://api.coingecko.com/api/v3/coins/{crypto}/market_chart?vs_currency={devise}&days=30"
response_history = requests.get(url_history).json()

# Extraire les prix et les dates
prices = response_history['prices']  # liste de [timestamp, prix]
dates = [datetime.fromtimestamp(p[0]/1000) for p in prices]  # convertir timestamp ms en datetime
prix = [p[1] for p in prices]

# Créer DataFrame
df = pd.DataFrame({"Date": dates, "Prix": prix})

# Graphique interactif
fig = px.line(df, x="Date", y="Prix", title=f"Historique 30 jours de {crypto} en {devise.upper()}")
st.plotly_chart(fig)
