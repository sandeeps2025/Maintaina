"""Small legacy-compatible model helper.

The production workflow lives in ``app.py`` and persists its preprocessing
pipeline alongside the estimator, so real uploaded datasets remain consistent
between training and prediction.
"""
from sklearn.ensemble import RandomForestClassifier


class ModelFactory:
    def __init__(self):
        self.models = {}

    def train_random_forest(self, X_train, y_train):
        model = RandomForestClassifier(
            n_estimators=180, random_state=42, n_jobs=1, class_weight="balanced"
        )
        model.fit(X_train, y_train)
        self.models["random_forest"] = model
        return model
