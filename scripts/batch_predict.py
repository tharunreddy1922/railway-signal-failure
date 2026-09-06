"""
Batch Prediction Script
======================
Make predictions for multiple signal failures at once
"""

import pandas as pd
import numpy as np
import joblib
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '/home/claude/railway_project')

# Load model and features
model = joblib.load('/home/claude/railway_project/models/repair_time_model.pkl')
scaler = joblib.load('/home/claude/railway_project/models/scaler.pkl')
feature_cols = joblib.load('/home/claude/railway_project/models/feature_cols.pkl')

# Example batch of new failures
batch_data = pd.DataFrame([
    {
        'failure_type': 'Track Circuit',
        'location': 'Waterloo',
        'weather': 'Rainy',
        'temperature_celsius': 10,
        'hour': 14,
        'is_peak_hour': 0,
        'is_weekend': 0,
        'is_rainy': 1
    },
    {
        'failure_type': 'Power Supply',
        'location': 'King\'s Cross',
        'weather': 'Clear',
        'temperature_celsius': 18,
        'hour': 8,
        'is_peak_hour': 1,
        'is_weekend': 0,
        'is_rainy': 0
    },
    {
        'failure_type': 'Software/Electronics',
        'location': 'Liverpool Street',
        'weather': 'Snowy',
        'temperature_celsius': -2,
        'hour': 16,
        'is_peak_hour': 1,
        'is_weekend': 1,
        'is_rainy': 1
    }
])

print("=" * 80)
print("BATCH PREDICTION RESULTS")
print("=" * 80)

# Generate predictions
for idx, row in batch_data.iterrows():
    print(f"\nFailure #{idx + 1}")
    print(f"{'─' * 60}")
    print(f"Location: {row['location']}")
    print(f"Failure Type: {row['failure_type']}")
    print(f"Weather: {row['weather']}")
    print(f"Temperature: {row['temperature_celsius']}°C")
    print(f"Time: {row['hour']:02d}:00")
    
    # Prepare features (same as app.py)
    input_data = {}
    input_data['hour'] = row['hour']
    input_data['temperature_celsius'] = row['temperature_celsius']
    input_data['is_peak_hour'] = row['is_peak_hour']
    input_data['is_weekend'] = row['is_weekend']
    input_data['is_rainy'] = row['is_rainy']
    input_data['location_encoded'] = ord(row['location'][0]) % 25  # Simple encoding
    input_data['month'] = datetime.now().month
    
    # One-hot encode
    for col in feature_cols:
        input_data[col] = 0
    
    input_data[f'failure_type_{row["failure_type"]}'] = 1
    input_data[f'weather_{row["weather"]}'] = 1
    
    # Predict
    df_input = pd.DataFrame([input_data])
    for col in feature_cols:
        if col not in df_input.columns:
            df_input[col] = 0
    
    X_input = df_input[feature_cols]
    X_scaled = scaler.transform(X_input)
    repair_time = max(20, model.predict(X_scaled)[0])
    
    # Output
    resume_time = datetime.now() + timedelta(minutes=int(repair_time))
    print(f"\n⏱️  ESTIMATED REPAIR TIME: {repair_time:.0f} minutes")
    print(f"📍 EXPECTED RESUMPTION: {resume_time.strftime('%H:%M')}")
    print(f"📊 CONFIDENCE: ±19 minutes")

print("\n" + "=" * 80)
print("✓ Batch prediction complete")
print("=" * 80)
