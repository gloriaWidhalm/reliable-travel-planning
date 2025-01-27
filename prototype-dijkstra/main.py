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
# We have a dictionary with the nodes as keys and the values are an array with tuples (departure_time, neighbor, arrival_time, trip identifier)
# times in minutes
# @todo: define time period -> probably one day makes sense, adjust train identifier

# graph = \
# This is based on the discussion about how the data structure should/could look like with the actual departure and arrival times
#     {
#         # departure node (=Liestal) -> [(scheduled departure_time, neighbor station, scheduled arrival_time, trip identifier, actual departure times, actual arrival times)]
#         # @todo -> add reliability of the connection
#     'Liestal': [
#         # we need all possible trips for each station within the 24 hours time period that we chose (on our reference day)
#         # [487, 489] -> actual departure times, [505, 506] -> actual arrival times
#         (487, 'Olten', 505, 'IC6_1', [487, 489], [505, 506]),
#         (502, 'Olten', 512, 'IC6_2', [502, 504], [512, 513])
#         # idea -> how to structure the actual departure and arrival times
#         # (departure time, arrival time)
#         # [(487, 505), (489, 506)] -> for each actual departure time, we have the actual arrival time as a tuple
#     ],

graph = \
    {
        # departure node (=Liestal) -> [(scheduled departure_time, neighbor station, scheduled arrival_time, trip identifier)]
        # @todo -> add reliability of the connection
    'Liestal': [(487, 'Olten', 505, 'IC6')],
     'Basel SBB': [(475, 'Liestal', 486, 'IC6')],
     'Olten': [(509, 'Bern', 536, 'IC6'), (451, 'Bern', 478, 'IC8')],
     'Bern': [(547, 'Thun', 565, 'IC6'), (487, 'Thun', 505, 'IC8')],
     'Thun': [(566, 'Spiez', 576, 'IC6'), (506, 'Spiez', 516, 'IC8')],
     'Spiez': [(576, 'Visp', 602, 'IC6'), (516, 'Visp', 542, 'IC8')],
     'Visp': [(603, 'Brig', 611, 'IC6'), (543, 'Brig', 551, 'IC8')],
     'Brig': [],
     'Aarau': [(438, 'Olten', 447, 'IC8')],
     'Zürich HB': [(404, 'Aarau', 436, 'IC8')]
    }
stops = [{'stop_name': 'Zürich HB', 'stop_lat': 47.378177, 'stop_lon': 8.540212},
         {'stop_name': 'Aarau', 'stop_lat': 47.39136, 'stop_lon': 8.051274},
         {'stop_name': 'Olten', 'stop_lat': 47.351935, 'stop_lon': 7.9077},
         {'stop_name': 'Bern', 'stop_lat': 46.948832, 'stop_lon': 7.439131},
         {'stop_name': 'Thun', 'stop_lat': 46.754853, 'stop_lon': 7.629606},
         {'stop_name': 'Spiez', 'stop_lat': 46.686396, 'stop_lon': 7.680103},
         {'stop_name': 'Visp', 'stop_lat': 46.294029, 'stop_lon': 7.881465},
         {'stop_name': 'Brig', 'stop_lat': 46.319423, 'stop_lon': 7.988095},
         {'stop_name': 'Basel SBB', 'stop_lat': 47.547412, 'stop_lon': 7.589563},
         {'stop_name': 'Liestal', 'stop_lat': 47.484461, 'stop_lon': 7.731367}]
# map stops for graph visualization: {"stop_name": [stop_lat, stop_lon]}
stops_map = {stop['stop_name']: [stop['stop_lon'], stop['stop_lat']] for stop in stops}

# initialize graph G (with graph class)
G = Graph(graph=graph)

# Example: shortest path from B to D
shortest_time, shortest_path = G.dijkstra("Bern", "Brig", 400)
print(f"Earliest arrival time from B to D is {shortest_time}")
print_path(shortest_path)

# get edges that are part of the shortest path
# @TODO fix that -> get the train identifier for the first edge
shortest_path[0] = (shortest_path[0][0], shortest_path[0][1], shortest_path[0][2], shortest_path[1][3])  #
edges_shortest_path = [(shortest_path[i][1], shortest_path[i + 1][1], shortest_path[i][3]) for i in range(len(shortest_path) - 1)]
# get edges that are not part of the shortest path
edges_not_shortest_path = [(node, edge[1], edge[3]) for node in graph for edge in graph[node] if (node, edge[1], edge[3]) not in edges_shortest_path]


def plot_graph(graph, pos=stops_map):
    """
    Plot the graph using networkx and matplotlib
    Based on: https://networkx.org/documentation/stable/auto_examples/drawing/plot_multigraphs.html
    """

    def _draw_labeled_multigraph(G, attr_name, pos, ax=None):
        """
        Length of connectionstyle must be at least that of a maximum number of edges
        between a pair of nodes. This number is maximum one-sided connections
        for directed graph and maximum total connections for undirected graph.
        """
        # Adjust the connectionstyle curvature
        max_edges = max(len(G[u][v]) for u, v in G.edges())
        connectionstyle = [f"arc3,rad={r}" for r in it.accumulate([0.15] * max_edges)]

        # pos = nx.spring_layout(G)
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=450, node_color="skyblue")
        # draw labels of nodes outside the nodes
        # Draw node labels outside the nodes
        offset = 0.035  # Adjust this value to control the distance of the labels from the nodes
        label_pos = {node: (x, y + offset) for node, (x, y) in pos.items()}
        nx.draw_networkx_labels(
            G,
            label_pos,
            font_size=10,
            font_color="black",
            ax=ax,
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="black", lw=0.5, alpha=0.9),
        )
        nx.draw_networkx_edges(
            G, pos, edge_color="grey", connectionstyle=connectionstyle, ax=ax, arrows=True, arrowsize=14
        )
        # nx.draw_networkx(G, pos)

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
            font_size=10,
            bbox=dict(boxstyle="round,pad=0.1", fc="white", ec=None, lw=0.5, alpha=1),
            ax=ax,
        )

    G = nx.MultiDiGraph()
    for node in graph:
        G.add_node(node)
        for (departure_time, neighbor, arrival_time, identifier) in graph[node]:
            G.add_edge(node, neighbor, identifier=identifier, departure_time=departure_time, arrival_time=arrival_time)
    _draw_labeled_multigraph(G, "identifier", pos)
    plt.show()

    def _draw_labeled_multigraph_v2(G, attr_name, pos, ax=None):
        """
        Draws a labeled multigraph with better visual adjustments.
        """
        # Adjust the connectionstyle curvature
        max_edges = max(len(G[u][v]) for u, v in G.edges())
        connectionstyle = [f"arc3,rad={r}" for r in it.accumulate([0.15] * max_edges)]

        # Draw nodes and labels
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=500, node_color="skyblue", edgecolors="black")
        nx.draw_networkx_labels(G, pos, font_size=10, font_color="black", ax=ax)

        # Draw edges with adjusted connection styles
        for i, (u, v, k) in enumerate(G.edges(keys=True)):
            nx.draw_networkx_edges(
                G,
                pos,
                edgelist=[(u, v)],
                edge_color="grey",
                connectionstyle=connectionstyle[i % len(connectionstyle)],
                ax=ax,
                arrows=True,
                arrowsize=14,
            )

        # Draw edge labels
        labels = {
            (u, v, k): f"{attrs[attr_name]}"
            for u, v, k, attrs in G.edges(keys=True, data=True)
        }
        for (u, v, k), label in labels.items():
            print((u, v, k), label)
        nx.draw_networkx_edge_labels(
            G,
            pos,
            edge_labels=labels,
            font_size=8,
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="black", lw=0.5, alpha=0.9),
            ax=ax,
        )

    # Example graph creation
    G = nx.MultiDiGraph()
    for node in graph:
        G.add_node(node)
        for departure_time, neighbor, arrival_time, identifier in graph[node]:
            G.add_edge(node, neighbor, identifier=identifier, departure_time=departure_time, arrival_time=arrival_time)

    # Adjust layout for better visualization
    pos = stops_map
    fig, ax = plt.subplots(figsize=(10, 8))  # Adjust figure size
    # _draw_labeled_multigraph_v2(G, "identifier", pos, ax=ax)
    # plt.show()


plot_graph(graph)
