import igraph, networkx, numpy, operator, pylab, random, sys

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import igraph as ig



# Function to create a small network for testing
def create_small_network():
    # Create a simple directed graph with NetworkX
    G = nx.DiGraph()
    # Add nodes and edges (for example: 4 nodes, 5 edges)
    edges = [(0, 1), (1, 2), (2, 3), (3, 0), (1, 3)]
    G.add_edges_from(edges)
    return G

# Function to plot the network
def plot_network(G, title="Small Network"):
    pos = nx.spring_layout(G)  # Positions for all nodes
    plt.figure(figsize=(5, 5))
    nx.draw(G, pos, with_labels=True, node_color="lightblue", edge_color="gray", node_size=700, font_size=15)
    plt.title(title)
    plt.show()

# Function to calculate robustness (number of nodes reachable from a random node)
def calculate_robustness(G, iterations=5):
    robustness_scores = []
    for i in range(iterations):
        start_node = np.random.choice(list(G.nodes))
        reachable_nodes = nx.single_source_shortest_path_length(G, start_node)
        robustness_scores.append(len(reachable_nodes))
    return np.mean(robustness_scores)

# Main code
if __name__ == "__main__":
    # Create and plot a small network
    G = create_small_network()
    plot_network(G, title="Test Network")

    # Calculate and print robustness score
    avg_reachability = calculate_robustness(G, iterations=5)
    print(f"Average Reachability (Robustness Score) over 5 iterations: {avg_reachability}")


# 1st Install this libraries using pip. Check out Quito's code
print("Success")

# To run
# Mac:
# Windows: py robustness_sample.py