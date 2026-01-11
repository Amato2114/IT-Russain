from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np

class MLModels:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.model = None

    def train_model(self):
        # Simple linear regression on index vs value
        self.model = LinearRegression()
        X = self.data.index.values.reshape(-1, 1)
        y = self.data['value'].values
        self.model.fit(X, y)

    def predict(self, X):
        if self.model is None:
            raise ValueError("Model not trained")
        return self.model.predict(X)