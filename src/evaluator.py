# src/evaluator.py
from sklearn.metrics import classification_report, confusion_matrix

class ModelEvaluator:
    def evaluate(self, model, X_test, y_test):
        y_pred = model.predict(X_test)

        report = classification_report(
            y_test,
            y_pred,
            output_dict=True
        )

        return {
            "report": report,
            "confusion_matrix": confusion_matrix(y_test, y_pred)
        }