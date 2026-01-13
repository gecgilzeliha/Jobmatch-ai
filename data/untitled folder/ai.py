from sklearn.datasets import make_blobs
import matplotlib.pyplot as plt

# Generate sample data using make_blobs
X, y = make_blobs(
    n_samples=200, 
    centers=5, 
    cluster_std=1.0, 
    random_state=100
    )

# Plot the data

# X[:,0] x coordinates
# X[:,1] y coordinates
# y is a list of cluster ids

plt.figure()
plt.scatter(X[:, 0], X[:, 1], c=y, cmap='viridis', edgecolor='k')
plt.title("Example of make_blobs with sklearn")
plt.xlabel("Feature 1")
plt.ylabel("Feature 2")
plt.show()

