# api/app.py
from fastapi import FastAPI
import pandas as pd
import joblib
from pathlib import Path

from src.input_analyzer import InputAnalyzer
from src.preprocessor import Preprocessor
from src.feature_extractor import FeatureExtractor
from src.predictor import AttackPredictor

app = FastAPI(title="IDPS ML API")

# ===== Path safe =====
BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "rf_model.pkl"
SCALER_PATH = BASE_DIR / "models" / "scaler.pkl"

# Load artifacts
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

# Init pipeline
predictor = AttackPredictor(model)
analyzer = InputAnalyzer()

preprocessor = Preprocessor()
preprocessor.scaler = scaler

extractor = FeatureExtractor()


@app.post("/predict")
def predict(data: dict):
    df = pd.DataFrame([data])

    df = analyzer.validate_dataframe(df)
    X = preprocessor.transform(df)
    X = extractor.extract(X)

    result = predictor.predict(X)
    print(" result:", result, type(result))
    return {
        "decision": result["decision"],
        "risk": result["risk"],
        "probabilities": result["probabilities"],
    }