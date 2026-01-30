import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pickle
import os

# Read the CSV file
csv_path = os.path.join(os.path.dirname(__file__), 'Recomender', 'Crop_data.csv')
data = pd.read_csv(csv_path)

# Display the data info
print("Data shape:", data.shape)
print("Columns:", data.columns.tolist())
print("\nFirst few rows:")
print(data.head())

# Separate features and target
X = data[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'soil_type']]
y = data['crop']

# Encode soil_type (convert categorical to numeric)
le_soil = LabelEncoder()
X['soil_type'] = le_soil.fit_transform(X['soil_type'])

print("\nSoil type encoding:")
for i, soil_type in enumerate(le_soil.classes_):
    print(f"  {soil_type}: {i}")

print("\nFeatures shape:", X.shape)
print("Target shape:", y.shape)
print("\nFeatures used:", X.columns.tolist())

# Train Random Forest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

print("\nModel trained successfully!")
print("Model accuracy (training):", model.score(X, y))

# Save the model
model_path = os.path.join(os.path.dirname(__file__), 'Recomender', 'RandomForest.pkl')
with open(model_path, 'wb') as f:
    pickle.dump(model, f)

print(f"Model saved to: {model_path}")
print("\nDone! The model now supports 8 features including soil_type.")
