"""
RAILWAY SIGNAL FAILURE PREDICTION WEB APP
==========================================

Real-time prediction dashboard for repair time and passenger communication.
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import datetime, timedelta
import json
import os

# Get the directory of the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Page configuration
st.set_page_config(
    page_title="Railway Signal Failure Predictor",
    page_icon="🚂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1A3A52;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 5px solid #3B82F6;
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

# Title and description
st.markdown('<div class="main-header">🚂 Railway Signal Failure Predictor</div>', unsafe_allow_html=True)
st.markdown("**AI-Powered Repair Time Estimation & Passenger Communication System**")

# Load model and data
@st.cache_resource
def load_model():
    # Use relative paths
    model_path = os.path.join(BASE_DIR, 'models', 'repair_time_model.pkl')
    scaler_path = os.path.join(BASE_DIR, 'models', 'scaler.pkl')
    feature_cols_path = os.path.join(BASE_DIR, 'models', 'feature_cols.pkl')
    model_info_path = os.path.join(BASE_DIR, 'models', 'model_info.json')
    
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    feature_cols = joblib.load(feature_cols_path)
    with open(model_info_path) as f:
        model_info = json.load(f)
    return model, scaler, feature_cols, model_info

@st.cache_data
def load_historical_data():
    data_path = os.path.join(BASE_DIR, 'data', 'signal_failures_raw.csv')
    df = pd.read_csv(data_path)
    return df

try:
    model, scaler, feature_cols, model_info = load_model()
    historical_df = load_historical_data()
except Exception as e:
    st.error(f"❌ Error loading model or data: {str(e)}")
    st.error(f"Make sure you're in the correct folder with 'models/' and 'data/' subfolders")
    st.stop()

# Sidebar - Model Info
with st.sidebar:
    st.markdown("### 📊 Model Information")
    st.markdown(f"""
    **Model Type:** {model_info['model_type']}
    
    **Performance Metrics:**
    - R² Score: {model_info['r2_score']:.1%}
    - Mean Absolute Error: ±{model_info['mae']:.0f} min
    - Root Mean Squared Error: {model_info['rmse']:.0f} min
    
    **Training Data:**
    - Failures analyzed: 1,000
    - Date range: 2022-2025
    - Locations: 25 UK stations
    """)
    
    st.markdown("---")
    st.markdown("### ℹ️ About This Tool")
    st.markdown("""
    This tool predicts signal failure repair times using:
    - **Failure type** (track circuit, interlocking, etc.)
    - **Weather conditions** (rain, snow, fog)
    - **Time of day** (peak vs. off-peak)
    - **Temperature**
    - **Location**
    
    Predictions are ±19 minutes accurate on average.
    """)

# Main Content
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
        
        location = st.selectbox(
            "Location",
            sorted(historical_df['location'].unique())
        )
        
        weather = st.selectbox(
            "Current Weather",
            ['Clear', 'Cloudy', 'Rainy', 'Foggy', 'Snowy', 'Stormy']
        )
    
    with col2:
        st.markdown("#### Environmental Factors")
        
        temperature = st.slider("Temperature (°C)", -10, 35, 15)
        
        hour = st.slider("Hour of Day (24h)", 0, 23, 14)
        
        is_peak = st.checkbox("Peak Hour (7-9am or 5-7pm)?")
        
        is_weekend = st.checkbox("Weekend?")
    
    st.markdown("---")
    
    # Make prediction
    if st.button("🔍 Predict Repair Time", use_container_width=True, type="primary"):
        # Prepare input features
        input_data = {}
        
        # Numeric features
        input_data['hour'] = hour
        input_data['temperature_celsius'] = temperature
        input_data['is_peak_hour'] = 1 if is_peak else 0
        input_data['is_weekend'] = 1 if is_weekend else 0
        input_data['is_rainy'] = 1 if weather in ['Rainy', 'Snowy', 'Stormy'] else 0
        input_data['location_encoded'] = list(historical_df['location'].unique()).index(location)
        input_data['month'] = datetime.now().month
        
        # Categorical features (one-hot encode)
        for col in feature_cols:
            input_data[col] = 0
        
        # Set the actual values
        input_data[f'failure_type_{failure_type}'] = 1
        input_data[f'weather_{weather}'] = 1
        input_data[f'day_of_week_{datetime.now().strftime("%A")}'] = 1
        
        # Create DataFrame with all features
        df_input = pd.DataFrame([input_data])
        
        # Ensure all features are present
        for col in feature_cols:
            if col not in df_input.columns:
                df_input[col] = 0
        
        X_input = df_input[feature_cols]
        X_scaled = scaler.transform(X_input)
        
        # Predict
        repair_time = model.predict(X_scaled)[0]
        repair_time = max(20, repair_time)  # Minimum 20 mins
        
        # Display prediction
        st.markdown("### 🎯 Prediction Result")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="prediction-box">', unsafe_allow_html=True)
            st.markdown(f"### {repair_time:.0f} minutes")
            st.markdown("**Estimated Repair Time**")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            error_margin = model_info['mae']
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f"**±{error_margin:.0f} minutes**")
            st.markdown(f"*Confidence interval (±1 std dev)*")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            resume_time = datetime.now() + timedelta(minutes=int(repair_time))
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f"**{resume_time.strftime('%H:%M')}**")
            st.markdown(f"*Expected service resumption*")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Passenger communication template
        st.markdown("### 📢 Automated Passenger Communication")
        
        passenger_message = f"""
**SIGNAL FAILURE AT {location.upper()}**

A signal failure has been detected at {location} station.

🔧 **Repair Status:**
- Current time: {datetime.now().strftime('%H:%M')}
- Estimated repair time: {repair_time:.0f} minutes
- **Expected service resumption: {resume_time.strftime('%H:%M')}**

📱 **What to do:**
- Please allow extra time for your journey
- Consider alternative routes
- Updates will be provided every 15 minutes
- For assistance, contact station staff

We apologize for the inconvenience.
        """
        
        st.info(passenger_message)
        
        st.markdown("---")
        
        # Key factors
        st.markdown("### 🔍 Factors Influencing This Prediction")
        
        factor_col1, factor_col2 = st.columns(2)
        
        with factor_col1:
            st.markdown("""
**Primary Factors:**
- **Failure Type:** Track circuits take longest (71 mins avg)
- **Weather:** Rain/snow adds 30-50% to repair time
- **Temperature:** Extreme cold increases complexity
            """)
        
        with factor_col2:
            st.markdown(f"""
**This Scenario:**
- Failure type: {failure_type}
- Weather: {weather}
- Temperature: {temperature}°C
- Peak hour: {"Yes" if is_peak else "No"}
            """)

# TAB 2: ANALYTICS
with tab2:
    st.markdown("### 📊 Historical Analysis")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Failures", len(historical_df), "3-year period")
    
    with col2:
        avg_repair = historical_df['repair_time_minutes'].mean()
        st.metric("Average Repair Time", f"{avg_repair:.0f} min", "±29.6 min std")
    
    with col3:
        total_passengers = historical_df['passengers_affected'].sum()
        st.metric("Passengers Affected", f"{total_passengers:,.0f}", "across all incidents")
    
    with col4:
        total_trains = historical_df['trains_affected'].sum()
        st.metric("Trains Affected", f"{total_trains:,.0f}", "total disruptions")
    
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
    st.markdown("### 📚 How to Use This Tool")
    
    st.markdown("""
**Step 1: Enter Signal Failure Details**
- Select the type of failure (track circuit, interlocking, etc.)
- Choose the location where the failure occurred
- Specify current weather conditions

**Step 2: Add Environmental Context**
- Input the current temperature
- Specify the hour of day
- Note if it's peak/off-peak and weekend/weekday

**Step 3: Get Prediction**
- Click "Predict Repair Time"
- Review the estimated repair duration
- View the confidence interval (±margin of error)

**Step 4: Communicate to Passengers**
- Copy the generated passenger message
- Update signage and announcements
- Send push notifications via mobile app

---

### 📖 Understanding the Results

**Repair Time:** The model predicts how long it will take to fix the signal.

**Confidence Interval:** Shows the range where the actual repair time likely falls (±19 mins for this model).

**Service Resumption:** Calculated as current time + predicted repair time.

---

### 🎯 Factors That Influence Repair Time

1. **Failure Type** (Highest Impact)
   - Track Circuit: ~71 mins
   - Interlocking: ~54 mins
   - Power Supply: ~45 mins
   - Software: ~39 mins

2. **Weather** (High Impact)
   - Clear: 48 mins
   - Rainy: 67 mins (40% longer)
   - Snowy: 79 mins (65% longer)

3. **Location** (Moderate Impact)
   - Inner London stations take slightly longer
   - Access and equipment availability vary

4. **Time of Day** (Low-Moderate Impact)
   - Peak hours slightly longer (+10%)
   - More staff available helps

---

### 💡 Tips for Accurate Predictions

✓ Specify the exact failure type if known
✓ Provide current weather conditions
✓ Use accurate temperature readings
✓ Consider time of day impact
✓ Allow for outliers - some repairs take longer than predicted

---

### 🔬 Model Details

- **Algorithm:** Linear Regression
- **Training Data:** 1,000 signal failures (2022-2025)
- **Features:** 25 variables (weather, location, time, failure type, etc.)
- **Accuracy:** R² = 0.285, MAE = ±19 minutes
- **Best For:** 0-120 minute repairs
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem; margin-top: 2rem;">
    <p>🚂 Railway Signal Failure Prediction System</p>
    <p>Built with Python, Streamlit, and Machine Learning | Data: 2022-2025</p>
    <p><em>Disclaimer: Predictions are estimates based on historical data. Actual repair times may vary.</em></p>
</div>
""", unsafe_allow_html=True)
