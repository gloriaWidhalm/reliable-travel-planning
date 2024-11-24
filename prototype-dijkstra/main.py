# This file contains code to run the simple Dijsktra pathfinder
from graph import Graph
import networkx as nx
import matplotlib.pyplot as plt
import itertools as it

def print_path(path):
    """
    Print the path in a human-readable way
    :param path: tuple with the path (departure_time, node, arrival_time, identifier)
    """
    for (departure_time, node, arrival_time, identifier) in path:
        if identifier is None:
            # The first edge is the source node
            print(f"Start at {path[0][1]} at {path[0][0]}")
        else:
            print(f"Take {identifier} to {node} at {departure_time} and arrive at {arrival_time}")


# Data structure (tuples sorted by departure time for faster access)
# We have a dictionary with the nodes as keys and the values are an array with tuples (departure_time, neighbor, arrival_time, identifier)
# times in minutes
graph = {
    "A": [(200, "B", 300, "B1"), (100, "B", 200, "B2"), (150, "C", 250, "C1"), (250, "C", 350, "C2")],
    "B": [(200, "A", 300, "A1"), (100, "A", 200, "A2"), (300, "D", 400, "D1"), (400, "D", 500, "D2")],
    "C": [(150, "A", 250, "A3"), (250, "A", 350, "A4")],
    "D": [(350, "A", 475, "A5"), (450, "A", 575, "A6"), (300, "B", 400, "B3"), (400, "B", 500, "B4")],
}

# initialize graph G (with graph class)
G = Graph(graph=graph)

# Example: shortest path from B to D
shortest_time, shortest_path = G.dijkstra("B", "D", 100)
print(f"Earliest arrival time from B to D is {shortest_time}")
print("Shortest path", shortest_path)

# Example: shortest path from B to C
shortest_time, shortest_path = G.dijkstra("B", "C", 100)
print(f"Earliest arrival time from B to C is {shortest_time}")
print("Shortest path", shortest_path)
print_path(shortest_path)


def plot_graph(graph):
    """
    Plot the graph using networkx and matplotlib
    Based on: https://networkx.org/documentation/stable/auto_examples/drawing/plot_multigraphs.html
    """
    def _draw_labeled_multigraph(G, attr_name, ax=None):
        """
        Length of connectionstyle must be at least that of a maximum number of edges
        between a pair of nodes. This number is maximum one-sided connections
        for directed graph and maximum total connections for undirected graph.
        """
        # Works with arc3 and angle3 connectionstyles
        connectionstyle = [f"arc3,rad={r}" for r in it.accumulate([0.16] * 4)]
        # connectionstyle = [f"angle3,angleA={r}" for r in it.accumulate([30] * 4)]

        pos = nx.spring_layout(G)
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=400, node_color="skyblue")
        nx.draw_networkx_labels(G, pos, font_size=16, ax=ax)
        nx.draw_networkx_edges(
            G, pos, edge_color="grey", connectionstyle=connectionstyle, ax=ax, arrows=True, arrowsize=14
        )

        labels = {
            tuple(edge): f"{attrs[attr_name]}"
            for *edge, attrs in G.edges(keys=True, data=True)
        }
        nx.draw_networkx_edge_labels(
            G,
            pos,
            labels,
            connectionstyle=connectionstyle,
            label_pos=0.5,
            font_color="black",
            bbox=dict(boxstyle="round,pad=0.1", fc="white", ec=None, lw=0.5, alpha=1),
            ax=ax,
        )

    G = nx.MultiDiGraph()
    for node in graph:
        G.add_node(node)
        for neighbor in graph[node]:
            for edge in graph[node][neighbor]:
                G.add_edge(node, neighbor, identifier=edge["identifier"], departure_time=edge["departure_time"], arrival_time=edge["arrival_time"])

    _draw_labeled_multigraph(G, "identifier")
    plt.show()

#plot_graph(graph)