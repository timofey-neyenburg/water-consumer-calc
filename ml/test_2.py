import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

from data import N_less_200, P_less_200, alpha_less_200

# Step 1: Simulate the 2D data
# --------------------------------------------
# A has 10 values (e.g., parameter like material type, angle, etc.)
# B has 100 values (e.g., time, temperature, frequency, etc.)
# a_vals = np.linspace(1, 10, 10)          # shape: (10,)
# b_vals = np.linspace(0, 50, 100)         # shape: (100,)
a_vals = np.array(N_less_200)
b_vals = np.array(P_less_200)
A, B = np.meshgrid(a_vals, b_vals, indexing='ij')  # Shape: (10, 100)

# Mathematical function (you can replace this with your own Z values)
# Z = sin(A) * log(1 + B)
# Z = np.sin(A) * np.log1p(B)              # Shape: (10, 100)
Z = np.array(alpha_less_200)

# Step 2: Prepare training data
# --------------------------------------------
# Convert grid to (A, B) → Z format
X = np.column_stack((A.ravel(), B.ravel()))  # Shape: (1000, 2)
y = Z.ravel()                                # Shape: (1000,)

# Step 3: Train-test split
# --------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 4: Train models
# --------------------------------------------
# Model 1: Random Forest Regressor
rf = RandomForestRegressor(n_estimators=1000, random_state=0)
rf.fit(X_train, y_train)

# Model 2: Neural Network (MLP) with feature scaling
mlp = make_pipeline(
    StandardScaler(),
    MLPRegressor(hidden_layer_sizes=(1000, 500), max_iter=2000, random_state=0)
)
mlp.fit(X_train, y_train)

# Step 5: Evaluate models
# --------------------------------------------
y_pred_rf = rf.predict(X_test)
y_pred_mlp = mlp.predict(X_test)

print("Random Forest MSE:", mean_squared_error(y_test, y_pred_rf))
print("MLP Regressor MSE:", mean_squared_error(y_test, y_pred_mlp))

# Step 6: Predict on new (A, B) values (possibly outside training range)
# --------------------------------------------
a_new = 197     # outside original range (1–10)
b_new = 0.67     # outside original range (0–50)
x_new = np.array([[a_new, b_new]])

z_pred_rf = rf.predict(x_new)[0]
z_pred_mlp = mlp.predict(x_new)[0]

# True value (if we know the underlying function)
z_true = np.sin(a_new) * np.log1p(b_new)

print(f"\nPredicting for A={a_new}, B={b_new}")
print(f"True Z = {z_true:.4f}")
print(f"RF Prediction = {z_pred_rf:.4f}")
print(f"MLP Prediction = {z_pred_mlp:.4f}")

# Step 7: (Optional) Visualization of original vs predicted
# --------------------------------------------
# Plot true vs predicted for MLP
plt.figure(figsize=(6, 6))
plt.scatter(y_test, y_pred_rf, alpha=0.5, label='RF')
plt.scatter(y_test, y_pred_mlp, alpha=0.5, label='MLP')
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', label='Ideal')
plt.xlabel("True Z")
plt.ylabel("Predicted Z")
plt.title("Model Prediction Accuracy")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()