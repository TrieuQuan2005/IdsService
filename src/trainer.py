# src/trainer.py
from sklearn.ensemble import RandomForestClassifier
import joblib
import numpy as np

class RandomForestTrainer:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=20,
            n_jobs=-1,
            random_state=42
        )

    def train(self, X, y):
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)

    def predict_with_confidence(self, X):
        preds = self.model.predict(X)
        probs = self.model.predict_proba(X)

        confidences = np.max(probs, axis=1)
        return preds, confidences

    def save(self, path):
        joblib.dump(self.model, path)

    def load(self, path):
        self.model = joblib.load(path)