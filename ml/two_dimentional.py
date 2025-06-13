import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

import matplotlib.pyplot as plt

# from mpl_toolkits.mplot3d import Axes3D

from data import N_less_200, P_less_200, alpha_less_200

# Step 2: Extract N and P values
N_values = np.array(N_less_200)
P_values = np.array(P_less_200)
Z_values = np.array(alpha_less_200)

# Step 4: Create training data (N, P) -> Z
N_grid, P_grid = np.meshgrid(N_values, P_values)
X = np.column_stack([N_grid.ravel(), P_grid.ravel()])
y = Z_values.ravel()

# Step 5: Train ML model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Step 6: Evaluate model
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print("Mean Squared Error:", mse)

# Step 7: Predict and plot (optional)
# Define a grid for plotting
N_plot = np.linspace(min(N_values), max(N_values), 100)
P_plot = np.linspace(min(P_values), max(P_values), 100)
N_mesh, P_mesh = np.meshgrid(N_plot, P_plot)
X_plot = np.column_stack([N_mesh.ravel(), P_mesh.ravel()])
Z_pred = model.predict(X_plot).reshape(N_mesh.shape)

# 3D Plot
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(N_mesh, P_mesh, Z_pred, cmap='viridis')
ax.set_xlabel('N')
ax.set_ylabel('P')
ax.set_zlabel('f(N, P)')
plt.title("Function Approximation using Random Forest")
plt.show()