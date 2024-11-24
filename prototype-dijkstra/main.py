# This file contains code to run the simple Dijsktra pathfinder
from graph import Graph
import networkx as nx
import matplotlib.pyplot as plt
import itertools as it

# graph data - nodes and edges
# this structure is an adjacency list (each node has its neighbors and the corresponding departure and arrival times)
# times in minutes

# @TODO: important aspect -> does this structure make sense for the problem? with the neighbors in a dictionary and the departure and arrival times in a list?
graph = {
    "A": {"B": [{"identifier": "B1", "departure_time": 200, "arrival_time": 300}, {"identifier": "B2", "departure_time": 100, "arrival_time": 200}],
          "C": [{"identifier": "C1", "departure_time": 150, "arrival_time": 250}, {"identifier": "C2", "departure_time": 250, "arrival_time": 350}]},
    "B": {"A": [{"identifier": "A1","departure_time": 200, "arrival_time": 300}, {"identifier": "A2","departure_time": 100, "arrival_time": 200}],
          "D": [{"identifier": "D1","departure_time": 300, "arrival_time": 400}, {"identifier": "D2","departure_time": 400, "arrival_time": 500}]},
    "C": {"A": [{"identifier": "A3","departure_time": 150, "arrival_time": 250}, {"identifier": "A4","departure_time": 250, "arrival_time": 350}]},
    "D": {"A": [{"identifier": "A5","departure_time": 350, "arrival_time": 475}, {"identifier": "A6","departure_time": 450, "arrival_time": 575}],
          "B": [{"identifier": "B3","departure_time": 300, "arrival_time": 400}, {"identifier": "B4","departure_time": 400, "arrival_time": 500}]},
}

# initialize graph G (with graph class)
G = Graph(graph=graph)

# Example: shortest path from B to D
shortest_time, shortest_path, edges_taken = G.dijkstra("B", "D", 100)
print(f"Shortest time from B to D is {shortest_time}")
print("Shortest path", shortest_path)
print("Edges taken", edges_taken)

# Example: shortest path from B to C
shortest_time, shortest_path, edges_taken = G.dijkstra("B", "C", 100)
print(f"Shortest time from B to C is {shortest_time}")
print("Shortest path", shortest_path)
print("Edges taken", edges_taken)


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
        connectionstyle = [f"arc3,rad={r}" for r in it.accumulate([0.15] * 4)]
        # connectionstyle = [f"angle3,angleA={r}" for r in it.accumulate([30] * 4)]

        pos = nx.spring_layout(G)
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=700, node_color="skyblue")
        nx.draw_networkx_labels(G, pos, font_size=20, ax=ax)
        nx.draw_networkx_edges(
            G, pos, edge_color="grey", connectionstyle=connectionstyle, ax=ax, arrows=True
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

plot_graph(graph)