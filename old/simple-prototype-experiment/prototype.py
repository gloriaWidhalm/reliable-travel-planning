# This file contains code to run the simple "shortest" pathfinder
from graph import Graph

# graph data - nodes and edges
# this structure is an adjacency list (each node has its neighbors and the corresponding weights)
graph = {
    "A": {"B": 3, "C": 3},
    "B": {"A": 3, "D": 3.5, "E": 2.8},
    "C": {"A": 3, "E": 2.8, "F": 3.5},
    "D": {"B": 3.5, "E": 3.1, "G": 10},
    "E": {"B": 2.8, "C": 2.8, "D": 3.1, "G": 7},
    "F": {"G": 2.5, "C": 3.5},
    "G": {"F": 2.5, "E": 7, "D": 10},
}

# initialize graph G (with graph class)
G = Graph(graph=graph)

# Example - get shortest distances from B
distances, predecessors = G.get_shortest_distances("B")
to_F = distances["F"]
print(f"Shortest distance from B to F is {to_F}")

shortest_path = G.shortest_path("B", "F")
print("shortest path", shortest_path)

shortest_path = G.shortest_path("A", "G")
print("shortest path", shortest_path)
