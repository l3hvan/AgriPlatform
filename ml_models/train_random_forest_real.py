import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Load the real merged dataset (ICRISAT crop data + GRACE groundwater + NDVI vegetation index)
df = pd.read_csv('ml_models/datasets/real_crop_data.csv')

# Random Forest needs numbers, not text - encode district into numeric codes
district_encoder = LabelEncoder()
df['district_encoded'] = district_encoder.fit_transform(df['district'])

# Features (inputs) and target (what it predicts)
X = df[['district_encoded', 'NDVI_mean', 'groundwater_anomaly']]
y = df['dominant_crop']

# Split: 80% to train on, 20% held back to honestly test accuracy on unseen data.
# stratify=y keeps the crop mix proportional in both halves - important since some crops are rare.
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Train the Random Forest
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Check accuracy on the held-back test data
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f"Model accuracy on test data: {accuracy * 100:.1f}%")
print()
print(classification_report(y_test, predictions, zero_division=0))

# Save the trained model AND the district encoder - both are needed later to make predictions
joblib.dump(model, 'ml_models/trained/random_forest_crop_model_real.pkl')
joblib.dump(district_encoder, 'ml_models/trained/district_encoder.pkl')

print("Model saved to ml_models/trained/random_forest_crop_model_real.pkl")
print("District encoder saved to ml_models/trained/district_encoder.pkl")