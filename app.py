import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
import google.generativeai as genai

# --- CONFIG ---
st.set_page_config(page_title="Agri-Weather Pro", layout="wide")

# 🔑 PASTE YOUR KEY HERE
GEMINI_API_KEY = "YOUR_KEY_HERE" 
genai.configure(api_key=GEMINI_API_KEY)

# --- DATA FETCHING ---
def get_weather_data(city):
    try:
        geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1").json()
        if "results" not in geo: return None
        res = geo["results"][0]
        lat, lon = res["latitude"], res["longitude"]
        
        # Pulling 7 days Past + 7 days Future
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode&past_days=7&timezone=auto"
        data = requests.get(url).json()
        return data, lat, lon, res['name']
    except: return None

# --- UI ---
st.title("🚜 Smart Agri-Weather Hub")
city_input = st.text_input("📍 Search Location", "Delhi")

payload = get_weather_data(city_input)

if payload:
    data, lat, lon, full_name = payload
    
    # --- NEW: CURRENT WEATHER METRICS (This shows the Temp/Weather clearly) ---
    today_temp = data["daily"]["temperature_2m_max"][7]
    today_min = data["daily"]["temperature_2m_min"][7]
    today_rain = data["daily"]["precipitation_sum"][7]
    
    st.markdown(f"### Current Status for **{full_name}**")
    col1, col2, col3 = st.columns(3)
    col1.metric("Max Temperature", f"{today_temp}°C")
    col2.metric("Min Temperature", f"{today_min}°C")
    col3.metric("Expected Rain", f"{today_rain} mm")
    
    st.markdown("---")

    # --- MAP SECTION ---
    st.subheader("Interactive Farming Map")
    m = folium.Map(location=[lat, lon], zoom_start=10)
    folium.Marker([lat, lon], popup=full_name).add_to(m)
    st_folium(m, width=1300, height=350)

    # --- TABS ---
    tab1, tab2, tab3 = st.tabs(["📊 Charts & History", "🌾 Agri-Alerts", "🤖 AI Weather Chat"])

    with tab1:
        st.write("### 14-Day Temperature & Rain Trends")
        df = pd.DataFrame({
            "Date": data["daily"]["time"],
            "Temp (°C)": data["daily"]["temperature_2m_max"],
            "Rain (mm)": data["daily"]["precipitation_sum"]
        })
        st.line_chart(df.set_index("Date")["Temp (°C)"])
        st.bar_chart(df.set_index("Date")["Rain (mm)"])

    with tab2:
        st.header("Farmer's Advisory")
        if today_temp > 30 and today_rain < 1:
            st.warning("⚠️ High Heat & No Rain: Suggest increasing irrigation to protect soil moisture.")
        elif today_rain > 10:
            st.error("⚠️ Heavy Rain Expected: Avoid fertilizers today to prevent runoff.")
        else:
            st.success("✅ Optimal conditions for regular farming activities.")

    with tab3:
        st.header("💬 AI Agricultural Assistant")
        if "messages" not in st.session_state: st.session_state.messages = []
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.write(msg["content"])

        if user_prompt := st.chat_input("Ask a question about your crops..."):
            st.session_state.messages.append({"role": "user", "content": user_prompt})
            with st.chat_message("user"): st.write(user_prompt)
            
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(f"In {full_name}, it is {today_temp}C. {user_prompt}")
            
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            with st.chat_message("assistant"): st.write(response.text)
else:
    st.error("Location not found! Please check spelling.")