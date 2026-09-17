import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

# Load the dataset generated in Step 15
df = pd.read_csv('ml_models/datasets/crop_data.csv')

# Random Forest needs numbers, not text - encode soil_type into numeric codes
soil_encoder = LabelEncoder()
df['soil_type_encoded'] = soil_encoder.fit_transform(df['soil_type'])

# Features (inputs the model learns from) and target (what it predicts)
X = df[['soil_type_encoded', 'rainfall_mm', 'temperature_c', 'humidity_percent']]
y = df['crop']

# Split: 80% to train on, 20% held back to honestly test accuracy on unseen data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the Random Forest
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Check accuracy on the held-back test data
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f"Model accuracy on test data: {accuracy * 100:.1f}%")

# Save the trained model AND the soil encoder - both are needed later to make predictions
joblib.dump(model, 'ml_models/trained/random_forest_crop_model.pkl')
joblib.dump(soil_encoder, 'ml_models/trained/soil_encoder.pkl')

print("Model saved to ml_models/trained/random_forest_crop_model.pkl")
print("Soil encoder saved to ml_models/trained/soil_encoder.pkl")