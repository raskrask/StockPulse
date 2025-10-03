"""
Tensorflowによる株価予測モデルの雛形
"""
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras

class StockPredictor:
    def __init__(self, input_shape):
        self.model = keras.Sequential([
            keras.layers.Dense(64, activation='relu', input_shape=(input_shape,)),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(1)
        ])
        self.model.compile(optimizer='adam', loss='mse')

    def train(self, X_train, y_train, epochs=10, batch_size=32):
        self.model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size)

    def predict(self, X):
        return self.model.predict(X)

# 使い方例
# df = pd.read_csv('data/stock.csv')
# X = df.drop('target', axis=1).values
# y = df['target'].values
# predictor = StockPredictor(X.shape[1])
# predictor.train(X, y)
# preds = predictor.predict(X)
