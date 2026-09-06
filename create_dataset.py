import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Create date range (3 years of data)
start_date = datetime(2022, 1, 1)
end_date = datetime(2025, 1, 1)
dates = pd.date_range(start=start_date, end=end_date, freq='D')

# Sample ~1000 signal failures over 3 years
num_failures = min(1000, len(dates) - 1)
failure_dates = sorted(random.sample(range(len(dates)), num_failures))
failure_datetimes = [dates[i] for i in failure_dates]

# UK railway locations (realistic)
locations = [
    'Waterloo', 'King\'s Cross', 'Liverpool Street', 'Victoria', 'Paddington',
    'Clapham Junction', 'Stratford', 'Whitechapel', 'Baker Street', 'Piccadilly Circus',
    'Southwark', 'London Bridge', 'Vauxhall', 'Elephant & Castle', 'Borough',
    'Bank', 'Moorgate', 'Farringdon', 'Holborn', 'Covent Garden',
    'Euston', 'St Pancras', 'King\'s Cross St Pancras', 'Angel', 'Old Street'
]

# Signal failure types (realistic UK railway failures)
failure_types = {
    'Track Circuit': 0.35,           # Most common (35%)
    'Interlocking': 0.20,            # 20%
    'Power Supply': 0.15,            # 15%
    'Software/Electronics': 0.15,    # 15%
    'Cable/Connector': 0.10,         # 10%
    'Other': 0.05                    # 5%
}

# Weather conditions
weather_conditions = {
    'Clear': 0.40,
    'Cloudy': 0.25,
    'Rainy': 0.20,
    'Foggy': 0.08,
    'Snowy': 0.04,
    'Stormy': 0.03
}

# Base repair times (minutes) by failure type
repair_times_base = {
    'Track Circuit': (60, 30),           # (mean, std dev) - rain makes it worse
    'Interlocking': (45, 25),
    'Power Supply': (40, 20),
    'Software/Electronics': (35, 15),
    'Cable/Connector': (50, 25),
    'Other': (55, 30)
}

# Create dataset
data = []
for failure_dt in failure_datetimes:
    location = random.choice(locations)
    failure_type = np.random.choice(
        list(failure_types.keys()),
        p=list(failure_types.values())
    )
    
    weather = np.random.choice(
        list(weather_conditions.keys()),
        p=list(weather_conditions.values())
    )
    
    # Base repair time
    mean_time, std_time = repair_times_base[failure_type]
    repair_time = max(20, int(np.random.normal(mean_time, std_time)))
    
    # Weather impact on repair time
    weather_multiplier = {
        'Clear': 1.0,
        'Cloudy': 1.05,
        'Rainy': 1.3,        # Rain significantly increases repair time
        'Foggy': 1.15,
        'Snowy': 1.4,        # Snow is worst
        'Stormy': 1.5
    }
    repair_time = int(repair_time * weather_multiplier[weather])
    
    # Time of day impact (rush hour more complex repairs?)
    hour = failure_dt.hour
    if 7 <= hour <= 9 or 17 <= hour <= 19:  # Peak hours
        repair_time = int(repair_time * 1.1)
    
    # Temperature (weather data)
    if failure_dt.month in [12, 1, 2]:
        temperature = int(np.random.normal(5, 4))
    elif failure_dt.month in [6, 7, 8]:
        temperature = int(np.random.normal(18, 3))
    else:
        temperature = int(np.random.normal(12, 4))
    
    # Passenger impact (rough estimate)
    base_passengers = np.random.randint(500, 3000)
    passenger_impact = int(base_passengers * (repair_time / 60))  # More time = more impact
    
    # Number of trains affected
    trains_affected = int(repair_time / 15) + random.randint(1, 3)
    
    data.append({
        'failure_datetime': failure_dt,
        'date': failure_dt.date(),
        'time': failure_dt.time(),
        'hour': failure_dt.hour,
        'day_of_week': failure_dt.day_name(),
        'location': location,
        'failure_type': failure_type,
        'weather': weather,
        'temperature_celsius': temperature,
        'is_peak_hour': 1 if (7 <= hour <= 9 or 17 <= hour <= 19) else 0,
        'is_weekend': 1 if failure_dt.weekday() >= 5 else 0,
        'repair_time_minutes': repair_time,
        'passengers_affected': passenger_impact,
        'trains_affected': trains_affected,
        'is_rainy': 1 if 'Rain' in weather or 'Snow' in weather or 'Storm' in weather else 0
    })

# Create DataFrame
df = pd.DataFrame(data)

# Add month and season
df['month'] = pd.to_datetime(df['date']).dt.month
df['season'] = df['month'].map({
    12: 'Winter', 1: 'Winter', 2: 'Winter',
    3: 'Spring', 4: 'Spring', 5: 'Spring',
    6: 'Summer', 7: 'Summer', 8: 'Summer',
    9: 'Autumn', 10: 'Autumn', 11: 'Autumn'
})

# One-hot encode categorical variables
df_encoded = pd.get_dummies(df, columns=['failure_type', 'weather', 'day_of_week', 'season'], drop_first=True)

print(f"Dataset created: {len(df)} signal failures")
print(f"\nDataset shape: {df.shape}")
print(f"\nColumns: {list(df.columns)}")
print(f"\nSample data:\n{df.head()}")
print(f"\nRepair time statistics:\n{df['repair_time_minutes'].describe()}")

# Save both versions
df.to_csv('/home/claude/railway_project/data/signal_failures_raw.csv', index=False)
df_encoded.to_csv('/home/claude/railway_project/data/signal_failures_processed.csv', index=False)

print("\n✓ Datasets saved:")
print("  - data/signal_failures_raw.csv")
print("  - data/signal_failures_processed.csv")
