from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np

class Forecasting:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def forecast(self, periods=10):
        # Simple linear forecast
        model = LinearRegression()
        X = np.arange(len(self.data)).reshape(-1, 1)
        y = self.data['value'].values
        model.fit(X, y)
        future_X = np.arange(len(self.data), len(self.data) + periods).reshape(-1, 1)
        forecasted = model.predict(future_X)
        return forecasted