import numpy as np
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Linear like data generation
np.random.seed(66)
X = 2 * np.random.rand(100, 1)             # 100 samples, 1 feature
y = 4 + 3 * X + np.random.randn(100, 1)    # y = 4 + 3X + Gaussian noise

# Split the data into training and test sets
# X contains the features
# y contains the target
X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2, 
    random_state=99
)


# Create and train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test)

# Evaluate the model using Mean Squared Error
mse = mean_squared_error(y_test, y_pred)
print("Mean Squared Error:", mse)

# Print the learned parameters (slope and intercept)
print("Slope (coefficient):", model.coef_[0][0])
print("Intercept:", model.intercept_[0])

# (Optional) Plot the results
plt.scatter(X, y, color="blue", label="Data Points")
plt.plot(X_test, y_pred, color="red", label="Prediction on Test Set")
plt.title("Linear Regression")
plt.xlabel("X")
plt.ylabel("y")
plt.legend()
plt.show()
