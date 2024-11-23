# This file contains code to run the simple Dijsktra pathfinder
from graph import Graph

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
    "D": {"B": [{"identifier": "B3","departure_time": 300, "arrival_time": 400}, {"identifier": "B4","departure_time": 400, "arrival_time": 500}]},
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
    """
    import networkx as nx
    import matplotlib.pyplot as plt

    G = nx.DiGraph()
    for node in graph:
        G.add_node(node)
        for neighbor in graph[node]:
            for edge in graph[node][neighbor]:
                G.add_edge(node, neighbor, identifier=edge["identifier"], departure_time=edge["departure_time"], arrival_time=edge["arrival_time"])

    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True)
    edge_labels = nx.get_edge_attributes(G, 'identifier')

    # @TODO plot graph with all edges, now only some are shown (maybe overlapping?)
    # check this out (multigraph, multidigraph: https://networkx.org/documentation/stable/auto_examples/drawing/plot_multigraphs.html)

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.show()

plot_graph(graph)