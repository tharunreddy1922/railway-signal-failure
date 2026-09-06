import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import datetime, timedelta
import json
import os

st.set_page_config(page_title="Railway Signal Failure Predictor", page_icon="🚂", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_resource
def load_model():
    try:
        model = joblib.load(os.path.join(BASE_DIR, 'models', 'repair_time_model.pkl'))
        scaler = joblib.load(os.path.join(BASE_DIR, 'models', 'scaler.pkl'))
        feature_cols = joblib.load(os.path.join(BASE_DIR, 'models', 'feature_cols.pkl'))
        with open(os.path.join(BASE_DIR, 'models', 'model_info.json')) as f:
            model_info = json.load(f)
        return model, scaler, feature_cols, model_info
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None, None, None, None

@st.cache_data
def load_data():
    try:
        return pd.read_csv(os.path.join(BASE_DIR, 'data', 'signal_failures_raw.csv'))
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

model, scaler, feature_cols, model_info = load_model()
df = load_data()

if model is None or df is None:
    st.stop()

st.markdown('<h1 style="color:#1A3A52;">🚂 Railway Signal Failure Predictor</h1>', unsafe_allow_html=True)
st.markdown("**AI-Powered Repair Time Estimation System**")

with st.sidebar:
    st.markdown("### 📊 Model Information")
    st.markdown(f"**Type:** {model_info['model_type']}\n**R² Score:** {model_info['r2_score']:.1%}\n**MAE:** ±{model_info['mae']:.0f} min")

tab1, tab2, tab3 = st.tabs(["🎯 Prediction", "📈 Analytics", "📚 Info"])

with tab1:
    st.markdown("### Signal Failure Prediction")
    col1, col2 = st.columns(2)
    
    with col1:
        failure_type = st.selectbox("Failure Type", ['Track Circuit', 'Interlocking', 'Power Supply', 'Software/Electronics', 'Cable/Connector', 'Other'])
        location = st.selectbox("Location", sorted(df['location'].unique()))
        weather = st.selectbox("Weather", ['Clear', 'Cloudy', 'Rainy', 'Foggy', 'Snowy', 'Stormy'])
    
    with col2:
        temperature = st.slider("Temperature (°C)", -10, 35, 15)
        hour = st.slider("Hour of Day", 0, 23, 14)
        is_peak = st.checkbox("Peak Hour (7-9am or 5-7pm)?")
        is_weekend = st.checkbox("Weekend?")
    
    if st.button("🔍 Predict Repair Time", use_container_width=True, type="primary"):
        input_data = {
            'hour': hour, 'temperature_celsius': temperature, 'is_peak_hour': 1 if is_peak else 0,
            'is_weekend': 1 if is_weekend else 0, 'is_rainy': 1 if weather in ['Rainy', 'Snowy', 'Stormy'] else 0,
            'location_encoded': list(df['location'].unique()).index(location), 'month': datetime.now().month,
        }
        
        for col in feature_cols:
            input_data[col] = 0
        
        input_data[f'failure_type_{failure_type}'] = 1
        input_data[f'weather_{weather}'] = 1
        input_data[f'day_of_week_{datetime.now().strftime("%A")}'] = 1
        
        df_input = pd.DataFrame([input_data])
        for col in feature_cols:
            if col not in df_input.columns:
                df_input[col] = 0
        
        X_scaled = scaler.transform(df_input[feature_cols])
        repair_time = max(20, model.predict(X_scaled)[0])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Repair Time", f"{repair_time:.0f} min", "Estimated")
        col2.metric("Confidence", f"±{model_info['mae']:.0f} min", "Error margin")
        resume_time = datetime.now() + timedelta(minutes=int(repair_time))
        col3.metric("Resumption", resume_time.strftime('%H:%M'), "Expected time")
        
        st.info(f"**SIGNAL FAILURE AT {location.upper()}**\n\nEstimated repair: {repair_time:.0f} minutes\nExpected resumption: {resume_time.strftime('%H:%M')}\n\nPlease allow extra time for your journey.")

with tab2:
    st.markdown("### Historical Analysis")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Failures", len(df))
    col2.metric("Avg Repair", f"{df['repair_time_minutes'].mean():.0f} min")
    col3.metric("Passengers", f"{df['passengers_affected'].sum():,.0f}")
    col4.metric("Trains", f"{df['trains_affected'].sum():,.0f}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.bar_chart(df.groupby('failure_type')['repair_time_minutes'].mean().sort_values(ascending=False))
    with col2:
        st.bar_chart(df.groupby('weather')['repair_time_minutes'].mean().sort_values(ascending=False))

with tab3:
    st.markdown("### About This Tool\n\n**Factors affecting repair time:**\n- Failure type (track circuits take longest)\n- Weather (rain/snow add 30-65%)\n- Temperature (extreme cold harder)\n- Time of day (peak hours +10%)\n\n**Model:** Linear Regression | **Accuracy:** ±19 minutes | **Data:** 1000 failures (2022-2025)")