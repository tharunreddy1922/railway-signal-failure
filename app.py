import streamlit as st
import pandas as pd
import joblib
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Railway Predictor", page_icon="🚂", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_resource
def load_model():
    model = joblib.load(os.path.join(BASE_DIR, 'models', 'repair_time_model.pkl'))
    scaler = joblib.load(os.path.join(BASE_DIR, 'models', 'scaler.pkl'))
    feature_cols = joblib.load(os.path.join(BASE_DIR, 'models', 'feature_cols.pkl'))
    import json
    with open(os.path.join(BASE_DIR, 'models', 'model_info.json')) as f:
        info = json.load(f)
    return model, scaler, feature_cols, info

@st.cache_data
def load_data():
    return pd.read_csv(os.path.join(BASE_DIR, 'data', 'signal_failures_raw.csv'))

model, scaler, feature_cols, info = load_model()
df = load_data()

st.title("🚂 Railway Signal Failure Predictor")

with st.sidebar:
    st.write(f"**Model:** {info['model_type']}")
    st.write(f"**Accuracy:** ±{info['mae']:.0f} min")

tab1, tab2 = st.tabs(["Prediction", "Analytics"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        failure_type = st.selectbox("Failure Type", ['Track Circuit', 'Interlocking', 'Power Supply', 'Software/Electronics', 'Cable/Connector', 'Other'])
        location = st.selectbox("Location", sorted(df['location'].unique()))
        weather = st.selectbox("Weather", ['Clear', 'Cloudy', 'Rainy', 'Foggy', 'Snowy', 'Stormy'])
    
    with col2:
        temp = st.slider("Temperature (°C)", -10, 35, 15)
        hour = st.slider("Hour", 0, 23, 14)
        peak = st.checkbox("Peak Hour?")
        weekend = st.checkbox("Weekend?")
    
    if st.button("Predict", use_container_width=True, type="primary"):
        data = {'hour': hour, 'temperature_celsius': temp, 'is_peak_hour': 1 if peak else 0,
                'is_weekend': 1 if weekend else 0, 'is_rainy': 1 if weather in ['Rainy', 'Snowy', 'Stormy'] else 0,
                'location_encoded': list(df['location'].unique()).index(location), 'month': datetime.now().month}
        
        for col in feature_cols:
            data[col] = 0
        data[f'failure_type_{failure_type}'] = 1
        data[f'weather_{weather}'] = 1
        data[f'day_of_week_{datetime.now().strftime("%A")}'] = 1
        
        df_input = pd.DataFrame([data])
        for col in feature_cols:
            if col not in df_input.columns:
                df_input[col] = 0
        
        X = scaler.transform(df_input[feature_cols])
        repair_time = max(20, model.predict(X)[0])
        
        # FIXED: Calculate resumption time based on selected hour, not current time
        resume_hour = (hour + int(repair_time) // 60) % 24
        resume_min = int(repair_time) % 60
        resume_time_str = f"{resume_hour:02d}:{resume_min:02d}"
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Repair Time", f"{repair_time:.0f} min")
        col2.metric("Confidence", f"±{info['mae']:.0f} min")
        col3.metric("Resumption", resume_time_str)
        
        st.info(f"**SIGNAL FAILURE AT {location.upper()}**\n\nEstimated repair: {repair_time:.0f} minutes\nExpected resumption: {resume_time_str}\n\nPlease allow extra time for your journey.")

with tab2:
    st.write(f"Total failures: {len(df)}")
    st.write(f"Avg repair: {df['repair_time_minutes'].mean():.0f} min")
    st.bar_chart(df.groupby('failure_type')['repair_time_minutes'].mean())