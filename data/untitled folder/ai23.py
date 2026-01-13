import numpy as np

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

import matplotlib.pyplot as plt
import seaborn as sns

from sys import exit

# Load the Iris dataset
iris = load_iris()
X = iris.data   # shape (150, 4): [sepal length, sepal width, petal length, petal width]
y = iris.target # species labels (0=setosa, 1=versicolor, 2=virginica)
class_names = iris.target_names

# Split into training and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2, 
    random_state=99
)

# Create and train a Decision Tree Classifier
clf = DecisionTreeClassifier(random_state=99)
clf.fit(X_train, y_train)

# Make predictions on the test set
y_pred = clf.predict(X_test)

# Evaluate performance with accuracy score
accuracy = accuracy_score(y_test, y_pred)
print("Test Accuracy:", accuracy)

# Accuracy check
print("Predicted labels:", y_pred)
print("Actual labels:   ", y_test)

conf_mat = confusion_matrix(y_test, y_pred)

# Visualize the confusion matrix
plt.figure(figsize=(6, 4))
sns.heatmap(conf_mat, annot=True, cmap='Blues', 
            xticklabels=class_names, 
            yticklabels=class_names, 
            fmt='d')
plt.title("Confusion Matrix")
plt.xlabel("Predicted Class")
plt.ylabel("True Class")
plt.show()
