import numpy as np
import matplotlib.pyplot as plt

from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

from data import NP_more_200, alpha_more_200

# Your X and Y data
X = np.array(NP_more_200)
Y = np.array(alpha_more_200)

poly = PolynomialFeatures(degree=2, include_bias=False)
features = poly.fit_transform(X.reshape(-1, 1))

lr = LinearRegression()
lr.fit(features, Y)
predicted_y = lr.predict(features)

print(len(predicted_y), predicted_y)

plt.figure(figsize=(10, 6))
plt.title("Your first polynomial regression – congrats! :)", size=16)

plt.scatter(X, Y)
plt.plot(X, predicted_y, c="red")

plt.show()

# Create and train the ML model
# model = RandomForestRegressor(n_estimators=1000)
# model.fit(X, Y)
# 
# # Predict values
# X_pred = np.linspace(min(X), max(X), 100).reshape(-1, 1)
# Y_pred = model.predict(X_pred)
# 
# # Plot the result
# plt.plot(X, Y, 'o', label='Data points')
# plt.plot(X_pred, Y_pred, '-', label='ML Prediction')
# plt.legend()
# plt.show()