# src/predictor.py
import numpy as np

class AttackPredictor:
    def __init__(self, model, dos_threshold=0.3, warn_threshold=0.15):
        self.model = model
        self.dos_threshold = dos_threshold
        self.warn_threshold = warn_threshold

    def predict(self, X):
        probs = self.model.predict_proba(X)[0]
        classes = list(self.model.classes_)

        # lấy xác suất từng class
        proba_map = dict(zip(classes, probs))

        p_normal = proba_map.get("BENIGN", proba_map.get("Normal", 0.0))
        p_dos = proba_map.get("DoS", 0.0)

        # logic quyết định IDS
        if p_dos >= self.dos_threshold:
            decision = "DoS"
            risk = "HIGH"
        elif p_dos >= self.warn_threshold:
            decision = "SUSPICIOUS"
            risk = "MEDIUM"
        else:
            decision = "NORMAL"
            risk = "LOW"

        return {
            "decision": decision,
            "risk": risk,
            "probabilities": proba_map
        }