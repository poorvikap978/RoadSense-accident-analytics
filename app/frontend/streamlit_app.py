import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="RoadSense", layout="wide")
st.title("🚗 RoadSense: Accident Severity & Hotspot Analysis")

tab1, tab2, tab3 = st.tabs(["Predict Severity", "Hotspot Map", "Association Rules"])

# ---------------- TAB 1: PREDICTION ----------------
with tab1:
    st.subheader("Predict Accident Severity")

    col1, col2 = st.columns(2)
    with col1:
        temperature = st.slider("Temperature (°F)", -20, 120, 60)
        humidity = st.slider("Humidity (%)", 0, 100, 50)
        wind_speed = st.slider("Wind Speed (mph)", 0, 60, 10)
        visibility = st.slider("Visibility (mi)", 0, 10, 10)

    with col2:
        hour = st.slider("Hour of Day (0-23)", 0, 23, 12)
        is_night = st.checkbox("Night time")
        weather = st.selectbox("Weather Condition", ["Clear", "Rain", "Light Rain", "Overcast", "Fog", "Snow", "Other"])
        lat = st.number_input("Latitude", value=39.8)
        lng = st.number_input("Longitude", value=-98.5)

    if st.button("Predict Severity"):
        payload = {
            "temperature": temperature, "humidity": humidity, "wind_speed": wind_speed,
            "visibility": visibility, "hour": hour, "is_night": is_night,
            "weather": weather, "lat": lat, "lng": lng
        }
        try:
            response = requests.post("http://localhost:9000/predict", json=payload)
            result = response.json()
            if result['severity'] == "Major Severity":
                st.error(f"⚠️ Predicted: {result['severity']}")
            else:
                st.success(f"✅ Predicted: {result['severity']}")
            st.info(f"Assigned to hotspot cluster: {result['cluster']}")
            st.write(f"Model's confidence of Major Severity: {result.get('major_severity_probability', 'N/A')}")
        except Exception as e:
            st.error(f"Could not reach backend. Make sure Flask is running. Error: {e}")

    st.subheader("Recent Predictions")
    try:
        history = requests.get("http://localhost:9000/history").json()
        if history:
            st.dataframe(pd.DataFrame(history))
    except:
        st.write("No history available yet.")

# ---------------- TAB 2: HOTSPOT MAP ----------------
with tab2:
    st.subheader("Accident Hotspot Clusters")
    try:
        with open("kmeans_clusters_map.html", 'r', encoding='utf-8') as f:
            map_html = f.read()
        st.components.v1.html(map_html, height=600)
    except FileNotFoundError:
        st.warning("Run clustering.ipynb first to generate the map.")

# ---------------- TAB 3: ASSOCIATION RULES ----------------
with tab3:
    st.subheader("Top Rules Predicting Major Severity")
    try:
        rules = pd.read_csv("../../data/processed/apriori_rules.csv")
        severity_rules = rules[rules['consequents'].str.contains('Major_Severity')]
        severity_rules = severity_rules.sort_values('lift', ascending=False).head(10)
        st.dataframe(severity_rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']])
    except FileNotFoundError:
        st.warning("Run association.ipynb first to generate rules.")