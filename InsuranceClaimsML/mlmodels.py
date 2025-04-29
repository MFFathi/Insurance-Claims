import numpy as np
from collections import Counter

class StandardScaler:
    def __init__(self):
        self.mean = None
        self.std = None

    def fit(self, X):
        X = X.astype(np.float64)
        self.mean = np.mean(X, axis=0)
        self.std = np.std(X, axis=0)
        self.std[self.std == 0] = 1

    def transform(self, X):
        X = X.astype(np.float64)
        return (X - self.mean) / self.std

    def fit_transform(self, X):
        self.fit(X)
        return self.transform(X)

class KNN:
    def __init__(self, k=1, regression=True):
        self.k = k
        self.regression = regression
        self.X_train = None
        self.y_train = None
        self.scaler = StandardScaler()

    def fit(self, X, y):
        self.X_train = self.scaler.fit_transform(X)
        self.y_train = np.array(y)

    def predict(self, X):
        X = self.scaler.transform(X)
        predictions = [self._predict(x) for x in X]
        return np.array(predictions)

    def _predict(self, x):
        distances = np.linalg.norm(self.X_train - x, axis=1)
        k_indices = np.argsort(distances)[:self.k]
        k_nearest_values = self.y_train[k_indices]
        if self.regression:
            return np.mean(k_nearest_values)
        else:
            return Counter(k_nearest_values).most_common(1)[0][0]

class MLModule:
    def __init__(self):
        self.models = {}

    def add_model(self, name, model):
        if not isinstance(model, KNN):  # No 'from .mlmodels import KNN'
            raise TypeError("Model must be an instance of KNN.")
        self.models[name] = model

    def train(self, name, X, y):
        if name in self.models:
            print(f"Training model '{name}' with {len(X)} samples...")
            self.models[name].fit(X, y)
        else:
            raise ValueError(f"Model '{name}' not found.")

    def predict(self, name, X):
        if name in self.models:
            return self.models[name].predict(X)
        else:
            raise ValueError(f"Model '{name}' not found.")
