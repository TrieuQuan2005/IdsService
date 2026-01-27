# train.py
import pandas as pd
import joblib

from src.input_analyzer import InputAnalyzer
from src.preprocessor import Preprocessor
from src.feature_extractor import FeatureExtractor
from src.label_encoder import AttackLabelEncoder
from src.trainer import RandomForestTrainer

# 1. Load dataset
df = pd.read_csv("data/raw/CICIDS2017.csv")

# 2. Split X / y
X_raw = df.drop(columns=["Label"])
y_raw = df["Label"]

# 3. Validate + select features
input_analyzer = InputAnalyzer()
X_valid = input_analyzer.validate_dataframe(X_raw)

# 4. Encode labels
label_encoder = AttackLabelEncoder()
y = label_encoder.encode(y_raw)

mask = y.notna()
X_valid = X_valid[mask]
y = y[mask]

# 5. Preprocess (fit scaler)
preprocessor = Preprocessor()
X_scaled = preprocessor.fit_transform(X_valid)

# Save scaler
joblib.dump(preprocessor.scaler, "models/scaler.pkl")

# 6. Feature extractor (pass-through)
feature_extractor = FeatureExtractor()
X_final = feature_extractor.extract(X_scaled)

# 7. Train model
trainer = RandomForestTrainer()
trainer.train(X_final, y)

# 8. Save model
trainer.save("models/rf_model.pkl")

print("Training completed!")
print("Model saved: models/rf_model.pkl")
print("Scaler saved: models/scaler.pkl")