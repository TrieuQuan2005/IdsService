# src/preprocessor.py
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler

class Preprocessor:
    def __init__(self, scaler_path=None):
        self.scaler = StandardScaler()
        self.scaler_path = scaler_path

        if scaler_path:
            try:
                self.scaler = joblib.load(scaler_path)
            except FileNotFoundError:
                pass

    def fit_transform(self, x):
        x = self._clean(x)
        x_scaled = self.scaler.fit_transform(x)

        if self.scaler_path:
            joblib.dump(self.scaler, self.scaler_path)

        return x_scaled

    def transform(self, x):
        x = self._clean(x)
        return self.scaler.transform(x)

    def _clean(self, x):
        x = x.replace([np.inf, -np.inf], np.nan)
        return x.fillna(0)