import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline


from data import N_less_200, P_less_200, alpha_less_200


X_vals = []
Y_vals = []
Z_vals = []

for ind, v in enumerate(N_less_200):
    for ind2, v2 in enumerate(P_less_200):
        X_vals.append(v)
        Y_vals.append(v2)
        Z_vals.append(alpha_less_200[ind2][ind])

# Пример: ваши известные значения X, Y и Z
# X_vals = N_less_200
# Y_vals = P_less_200
# Z_vals = alpha_less_200

# Объединение X и Y в матрицу признаков
X_train = np.column_stack((X_vals, Y_vals))
y_train = np.array(Z_vals)

# Обучение модели
# model = LinearRegression()
# model.fit(X_train, y_train)

# model = RandomForestRegressor(n_estimators=100, random_state=0)
# model.fit(X_train, y_train)


# model = MLPRegressor(hidden_layer_sizes=(1000, 1000, 1000),  # 2 слоя по 100 нейронов
#                      activation='relu',
#                      solver='adam',
#                      max_iter=1000,
#                      random_state=42)
# 
# model.fit(X_train, y_train)


model = make_pipeline(
    StandardScaler(),
    SVR(kernel='rbf', C=100, epsilon=0.1)
)
model.fit(X_train, y_train)

# Предсказание на новых данных
X_new = np.array([[2, 0.4], [2, 0.5], [2, 0.8], [8, 0.316], [34, 0.8], [200, 0.8]])  # любые новые X и Y
Z_pred = model.predict(X_new)

print("Предсказанные значения Z:", Z_pred)

# from matplotlib import cm
# 
# fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
# 
# # Make data.
# X, Y = np.meshgrid(X_vals, Y_vals)
# Z = np.array(alpha_less_200)
# 
# surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
#                        linewidth=0, antialiased=False)
# 
# # Customize the z axis.
# ax.set_zlim(-1.01, 1.01)
# ax.zaxis.set_major_locator(LinearLocator(10))
# # A StrMethodFormatter is used automatically
# ax.zaxis.set_major_formatter('{x:.02f}')
# 
# # Add a color bar which maps values to colors.
# fig.colorbar(surf, shrink=0.5, aspect=5)
# 
# plt.show()
# 