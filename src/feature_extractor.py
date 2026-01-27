# src/feature_extractor.py
import pandas as pd

class FeatureExtractor:
    """
    Runtime feature validation module.
    Prevents abnormal values from corrupting model inference.
    """

    def extract(self, X: pd.DataFrame) -> pd.DataFrame:
        X = X.copy()

        # Clamp negative values (real-world robustness)
        X[X < 0] = 0

        return X