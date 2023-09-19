import matplotlib.pyplot as plt
from scipy.spatial import distance


def calculate_distance_matrix(df, metric="euclidean"):
    points = df[["x_int", "y_int"]].values
    return distance.cdist(points, points, metric=metric)


def cost_distance(distance_matrix, route):
    return distance_matrix[route[:-1], route[1:]].sum().item()


def plot_route(coords_df, route):
    df = coords_df.set_index("Node_ID").reindex(route).reset_index()
    _, ax = plt.subplots()
    ax.plot(df["x_int"], df["y_int"], color="gray", linewidth=1)
    ax.scatter(df["x_int"], df["y_int"], s=1)
    ax.set_title("plot route")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    plt.show()
