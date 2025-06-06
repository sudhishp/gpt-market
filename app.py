# Streamlit App: GPT-Based Market Summary Dashboard

import streamlit as st
import openai
import requests
from datetime import datetime, timedelta

# ---- Config ----
openai.api_key = st.secrets["OPENAI_API_KEY"]
FRED_API_KEY = st.secrets.get("FRED_API_KEY")

# ---- FRED API Helper ----
def get_fred_data(series_id):
    url = f"https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 1
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()["observations"]
        if data:
            return float(data[0]["value"])
    return None

# ---- Load Realtime Data from FRED ----
def get_realtime_data():
    return {
        "VIX": get_fred_data("VIXCLS"),
        "MOVE": get_fred_data("MOVEAVG"),
        "HY_OAS": get_fred_data("BAMLH0A0HYM2"),
        "TED_Spread": get_fred_data("TEDRATE"),
        "NFCI": get_fred_data("NFCI")
    }

# ---- GPT Summary Generator ----
def generate_summary(data):
    prompt = f"""
    You are a financial analyst AI. Summarize the current market conditions based on the following macro indicators:

    - VIX: {data['VIX']}
    - MOVE Index: {data['MOVE']}
    - High Yield OAS: {data['HY_OAS']}
    - TED Spread: {data['TED_Spread']}
    - Chicago Fed NFCI: {data['NFCI']}

    Classify sentiment as Bearish, Neutral, or Bullish. Provide a 3–5 sentence summary for a general audience.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a financial analyst."},
                  {"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

# ---- Streamlit UI ----
st.set_page_config(page_title="Market Sentiment AI Dashboard", layout="wide")
st.title("📈 GPT-Based Market Conditions Dashboard")

with st.spinner("Fetching real-time indicator data from FRED..."):
    data = get_realtime_data()

col1, col2, col3 = st.columns(3)
col1.metric("VIX", data['VIX'])
col2.metric("MOVE Index", data['MOVE'])
col3.metric("High Yield OAS", f"{data['HY_OAS']}%")

col4, col5 = st.columns(2)
col4.metric("TED Spread", f"{data['TED_Spread']}%")
col5.metric("NFCI", data['NFCI'])

if st.button("🔍 Generate Market Summary"):
    summary = generate_summary(data)
    st.subheader("📊 Market Insight Summary")
    st.markdown(summary)
else:
    st.info("Click the button above to analyze the current conditions using GPT.")
