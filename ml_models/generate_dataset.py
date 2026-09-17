import pandas as pd
import random

random.seed(42)

crop_profiles = {
    'Wheat':     {'rainfall': (60, 100),  'temp': (15, 25), 'humidity': (50, 70), 'soil': ['Loamy', 'Clay']},
    'Rice':      {'rainfall': (150, 300), 'temp': (22, 32), 'humidity': (70, 90), 'soil': ['Clay', 'Loamy']},
    'Maize':     {'rainfall': (80, 120),  'temp': (20, 30), 'humidity': (55, 75), 'soil': ['Loamy', 'Sandy']},
    'Cotton':    {'rainfall': (60, 110),  'temp': (25, 35), 'humidity': (40, 60), 'soil': ['Black', 'Sandy']},
    'Sugarcane': {'rainfall': (150, 250), 'temp': (24, 34), 'humidity': (65, 85), 'soil': ['Loamy', 'Black']},
}

rows = []
for crop, profile in crop_profiles.items():
    for _ in range(40):
        rows.append({
            'soil_type': random.choice(profile['soil']),
            'rainfall_mm': round(random.uniform(*profile['rainfall']), 1),
            'temperature_c': round(random.uniform(*profile['temp']), 1),
            'humidity_percent': round(random.uniform(*profile['humidity']), 1),
            'crop': crop,
        })

df = pd.DataFrame(rows)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)
df.to_csv('ml_models/datasets/crop_data.csv', index=False)

print(f"Created dataset with {len(df)} rows at ml_models/datasets/crop_data.csv")
print(df.head())