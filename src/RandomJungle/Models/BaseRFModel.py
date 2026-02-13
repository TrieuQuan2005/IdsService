from abc import ABC
from typing import List
import numpy as np
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


class BaseRFModel(ABC):

    def __init__(
        self,
        n_estimators: int = 300,
        max_depth: int | None = 20,
        min_samples_split: int = 5,
        min_samples_leaf: int = 2,
        max_features: str | float = "sqrt",
        bootstrap: bool = True,
        class_weight: str | dict | None = "balanced_subsample",
        random_state: int = 42,
    ):

        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            max_features=max_features,
            bootstrap=bootstrap,
            class_weight=class_weight,
            random_state=random_state,
            n_jobs=-1,
        )

        self._is_fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self._validate_input(X)
        self.model.fit(X, y)
        self._is_fitted = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        self._ensure_fitted()
        self._validate_input(X)
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        self._ensure_fitted()
        self._validate_input(X)
        return self.model.predict_proba(X)

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> float:
        preds = self.predict(X)
        return accuracy_score(y, preds)

    def save(self, path: str) -> None:
        joblib.dump(self.model, path)

    def load(self, path: str) -> None:
        self.model = joblib.load(path)
        self._is_fitted = True

    def feature_importance(self) -> List[float]:
        self._ensure_fitted()
        return self.model.feature_importances_.tolist()

    @staticmethod
    def _validate_input(X: np.ndarray) -> None:
        if not isinstance(X, np.ndarray):
            raise ValueError("Input must be numpy array")

        if len(X.shape) != 2:
            raise ValueError("Input must be 2D array")

    def _ensure_fitted(self):
        if not self._is_fitted:
            raise RuntimeError("Model is not fitted yet.")
