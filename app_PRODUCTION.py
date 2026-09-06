"""
RAILWAY SIGNAL FAILURE PREDICTION WEB APP
==========================================
Production-ready for Streamlit Cloud
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import datetime, timedelta
import json
import os
import sys

# Configure page FIRST
st.set_page_config(
    page_title="Railway Signal Failure Predictor",
    page_icon="🚂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Get base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load model with error handling
@st.cache_resource
def load_model():
    try:
        model_path = os.path.join(BASE_DIR, 'models', 'repair_time_model.pkl')
        scaler_path = os.path.join(BASE_DIR, 'models', 'scaler.pkl')
        feature_cols_path = os.path.join(BASE_DIR, 'models', 'feature_cols.pkl')
        model_info_path = os.path.join(BASE_DIR, 'models', 'model_info.json')
        
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        feature_cols = joblib.load(feature_cols_path)
        
        with open(model_info_path, 'r') as f:
            model_info = json.load(f)
        
        return model, scaler, feature_cols, model_info
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None, None, None, None

@st.cache_data
def load_historical_data():
    try:
        data_path = os.path.join(BASE_DIR, 'data', 'signal_failures_raw.csv')
        df = pd.read_csv(data_path)
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# Load data
model, scaler, feature_cols, model_info = load_model()
historical_df = load_historical_data()

# Check if data loaded
if model is None or historical_df is None:
    st.error("❌ Failed to load model or data. Please contact administrator.")
    st.stop()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1A3A52;
        margin-bottom: 1rem;
    }
    .prediction-box {
        background-color: #EFF6FF;
        padding: 2rem;
        border-radius: 1rem;
        border: 2px solid #3B82F6;
        text-align: center;
    }
    .metric-card {
        background-color: #F9FAFB;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-top: 4px solid #10B981;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">🚂 Railway Signal Failure Predictor</div>', unsafe_allow_html=True)
st.markdown("**AI-Powered Repair Time Estimation & Passenger Communication System**")

# Sidebar
with st.sidebar:
    st.markdown("### 📊 Model Information")
    st.markdown(f"""
    **Model Type:** {model_info['model_type']}
    
    **Performance:**
    - R² Score: {model_info['r2_score']:.1%}
    - Mean Error: ±{model_info['mae']:.0f} min
    - RMSE: {model_info['rmse']:.0f} min
    
    **Training Data:**
    - Failures: 1,000
    - Period: 2022-2025
    - Locations: 25 UK stations
    """)

# Main tabs
tab1, tab2, tab3 = st.tabs(["🎯 Prediction", "📈 Analytics", "📚 Documentation"])

# TAB 1: PREDICTION
with tab1:
    st.markdown("### Real-Time Signal Failure Prediction")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Incident Details")
        failure_type = st.selectbox(
            "Failure Type",
            ['Track Circuit', 'Interlocking', 'Power Supply', 
             'Software/Electronics', 'Cable/Connector', 'Other']
        )
        location = st.selectbox("Location", sorted(historical_df['location'].unique()))
        weather = st.selectbox("Weather", ['Clear', 'Cloudy', 'Rainy', 'Foggy', 'Snowy', 'Stormy'])
    
    with col2:
        st.markdown("#### Environmental Factors")
        temperature = st.slider("Temperature (°C)", -10, 35, 15)
        hour = st.slider("Hour of Day (24h)", 0, 23, 14)
        is_peak = st.checkbox("Peak Hour (7-9am or 5-7pm)?")
        is_weekend = st.checkbox("Weekend?")
    
    st.markdown("---")
    
    if st.button("🔍 Predict Repair Time", use_container_width=True, type="primary"):
        # Prepare input
        input_data = {
            'hour': hour,
            'temperature_celsius': temperature,
            'is_peak_hour': 1 if is_peak else 0,
            'is_weekend': 1 if is_weekend else 0,
            'is_rainy': 1 if weather in ['Rainy', 'Snowy', 'Stormy'] else 0,
            'location_encoded': list(historical_df['location'].unique()).index(location),
            'month': datetime.now().month,
        }
        
        # One-hot encode
        for col in feature_cols:
            input_data[col] = 0
        
        input_data[f'failure_type_{failure_type}'] = 1
        input_data[f'weather_{weather}'] = 1
        input_data[f'day_of_week_{datetime.now().strftime("%A")}'] = 1
        
        # Create DataFrame
        df_input = pd.DataFrame([input_data])
        for col in feature_cols:
            if col not in df_input.columns:
                df_input[col] = 0
        
        X_input = df_input[feature_cols]
        X_scaled = scaler.transform(X_input)
        
        # Predict
        repair_time = max(20, model.predict(X_scaled)[0])
        
        # Display results
        st.markdown("### 🎯 Prediction Result")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f'<div class="prediction-box"><h2>{repair_time:.0f} minutes</h2><p><b>Estimated Repair Time</b></p></div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'<div class="metric-card"><b>±{model_info["mae"]:.0f} minutes</b><br><em>Confidence interval</em></div>', unsafe_allow_html=True)
        
        with col3:
            resume_time = datetime.now() + timedelta(minutes=int(repair_time))
            st.markdown(f'<div class="metric-card"><b>{resume_time.strftime("%H:%M")}</b><br><em>Expected resumption</em></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Passenger message
        st.markdown("### 📢 Automated Passenger Communication")
        passenger_msg = f"""
**SIGNAL FAILURE AT {location.upper()}**

A signal failure has been detected at {location} station.

🔧 **Repair Status:**
- Estimated repair time: {repair_time:.0f} minutes
- Expected resumption: {resume_time.strftime('%H:%M')}

📱 **What to do:**
- Please allow extra time for your journey
- Consider alternative routes
- Updates provided every 15 minutes
- Contact station staff for assistance

We apologize for the inconvenience.
        """
        st.info(passenger_msg)

# TAB 2: ANALYTICS
with tab2:
    st.markdown("### 📊 Historical Analysis")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Failures", len(historical_df), "3-year period")
    col2.metric("Avg Repair Time", f"{historical_df['repair_time_minutes'].mean():.0f} min", "average")
    col3.metric("Passengers Affected", f"{historical_df['passengers_affected'].sum():,.0f}", "total")
    col4.metric("Trains Affected", f"{historical_df['trains_affected'].sum():,.0f}", "total")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Repair Time by Failure Type")
        repair_by_type = historical_df.groupby('failure_type')['repair_time_minutes'].mean().sort_values(ascending=False)
        st.bar_chart(repair_by_type)
    
    with col2:
        st.markdown("### Impact by Weather")
        repair_by_weather = historical_df.groupby('weather')['repair_time_minutes'].mean().sort_values(ascending=False)
        st.bar_chart(repair_by_weather)

# TAB 3: DOCUMENTATION
with tab3:
    st.markdown("""
    ### 📚 How to Use This Tool
    
    **Step 1: Enter Failure Details**
    - Select failure type (track circuit, interlocking, etc.)
    - Choose location
    - Specify weather conditions
    
    **Step 2: Environmental Context**
    - Temperature
    - Hour of day
    - Peak hour status
    - Weekend/weekday
    
    **Step 3: Get Prediction**
    - Click "Predict Repair Time"
    - View estimated duration
    - Copy passenger message
    
    ---
    
    ### 🎯 Key Factors
    
    **Failure Type Impact:**
    - Track Circuit: ~71 mins
    - Interlocking: ~54 mins
    - Power Supply: ~45 mins
    - Software: ~39 mins
    
    **Weather Impact:**
    - Clear: 48 mins
    - Rainy: 67 mins (+40%)
    - Snowy: 79 mins (+65%)
    
    **Model Details:**
    - Algorithm: Linear Regression
    - Training data: 1,000 failures (2022-2025)
    - Features: 25 variables
    - Accuracy: ±19 minutes average
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>🚂 Railway Signal Failure Prediction System</p>
    <p>Built with Python, Streamlit, Machine Learning</p>
</div>
""", unsafe_allow_html=True)
