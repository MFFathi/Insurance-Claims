import numpy as np

class MLModule:
    def __init__(self, model, X_min, X_max, denom, category_mappings, feature_names):
        self.model = model
        self.X_min = X_min
        self.X_max = X_max
        self.denom = denom
        self.category_mappings = category_mappings
        self.feature_names = feature_names

    def predict(self, X):
        return self.model.predict(X)
