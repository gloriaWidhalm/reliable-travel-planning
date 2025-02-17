import networkx as nx
import matplotlib.pyplot as plt
import itertools as it

# intermediate stops
stops = [
    {"stop_name": "Zürich HB", "stop_lat": 47.378177, "stop_lon": 8.540212},
    {"stop_name": "Aarau", "stop_lat": 47.39136, "stop_lon": 8.051274},
    {"stop_name": "Olten", "stop_lat": 47.351935, "stop_lon": 7.9077},
    {"stop_name": "Bern", "stop_lat": 46.948832, "stop_lon": 7.439131},
    {"stop_name": "Thun", "stop_lat": 46.754853, "stop_lon": 7.629606},
    {"stop_name": "Spiez", "stop_lat": 46.686396, "stop_lon": 7.680103},
    {"stop_name": "Visp", "stop_lat": 46.294029, "stop_lon": 7.881465},
    {"stop_name": "Brig", "stop_lat": 46.319423, "stop_lon": 7.988095},
    {"stop_name": "Basel SBB", "stop_lat": 47.547412, "stop_lon": 7.589563},
    {"stop_name": "Liestal", "stop_lat": 47.484461, "stop_lon": 7.731367},
]
# map stops for graph visualization: {"stop_name": [stop_lat, stop_lon]}
stops_map = {stop["stop_name"]: [stop["stop_lon"], stop["stop_lat"]] for stop in stops}


def plot_graph(
    graph,
    pos=stops_map,
    title=None,
    save=False,
    save_path=None,
    filename=None,
    edge_color=None,
    reset=True,
    additional_text=None,
):
    """
    Plot the graph using networkx and matplotlib
    Based on: https://networkx.org/documentation/stable/auto_examples/drawing/plot_multigraphs.html
    """
    # reset plot
    if reset:
        plt.clf()

    def _draw_labeled_multigraph(G, attr_name, pos, ax=None, edge_color=None):
        """
        Length of connectionstyle must be at least that of a maximum number of edges
        between a pair of nodes. This number is maximum one-sided connections
        for directed graph and maximum total connections for undirected graph.
        """
        # Adjust the connectionstyle curvature
        max_edges = max(len(G[u][v]) for u, v in G.edges())
        connectionstyle = [f"arc3,rad={r}" for r in it.accumulate([0.15] * max_edges)]

        # pos = nx.spring_layout(G)
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=500, node_color="skyblue")
        # draw labels of nodes outside the nodes
        # Draw node labels outside the nodes
        offset = 0.005  # Adjust this value to control the distance of the labels from the nodes
        label_pos = {node: (x, y + offset) for node, (x, y) in pos.items()}
        nx.draw_networkx_labels(
            G,
            label_pos,
            font_size=12,
            font_color="black",
            ax=ax,
            bbox=dict(
                boxstyle="round,pad=0.2", fc="white", ec="black", lw=0.5, alpha=0.9
            ),
        )
        edge_color_used = edge_color if edge_color is not None else "grey"
        nx.draw_networkx_edges(
            G,
            pos,
            edge_color=edge_color_used,
            connectionstyle=connectionstyle,
            ax=ax,
            arrows=True,
            arrowsize=14,
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
            font_size=12,
            bbox=dict(boxstyle="round,pad=0.1", fc="white", ec=None, lw=0.5, alpha=1),
            ax=ax,
        )

    def _draw_labeled_multigraph_v2(G, attr_name, pos, ax=None):
        """
        Draws a labeled multigraph with better visual adjustments.
        """
        # Adjust the connectionstyle curvature
        max_edges = max(len(G[u][v]) for u, v in G.edges())
        connectionstyle = [f"arc3,rad={r}" for r in it.accumulate([0.15] * max_edges)]

        # Draw nodes and labels
        nx.draw_networkx_nodes(
            G, pos, ax=ax, node_size=2000, node_color="skyblue", edgecolors="black"
        )
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
            font_size=10,
            bbox=dict(
                boxstyle="round,pad=0.2", fc="white", ec="black", lw=0.5, alpha=0.9
            ),
            ax=ax,
        )

    G = nx.MultiDiGraph()
    for node in graph:
        G.add_node(node)
        for departure_time, neighbor, arrival_time, identifier in graph[node]:
            G.add_edge(
                node,
                neighbor,
                identifier=identifier,
                departure_time=departure_time,
                arrival_time=arrival_time,
            )
    _draw_labeled_multigraph(G, "identifier", pos, edge_color=edge_color)

    # Set title if title is not None
    if title is not None:
        plt.title(title)

    # add additional text in the top left corner within the graph, smaller font
    if additional_text:
        plt.text(
            0.135, 0.7, additional_text, fontsize=8, transform=plt.gcf().transFigure
        )

    # save the plot if save is True
    if save:
        if save_path is None:
            save_path = "./visuals/"
        if filename is None:
            filename = "graph.png"
        file_path = save_path + filename
        plt.savefig(file_path)
    else:
        plt.show()

    # # Example graph creation
    # G = nx.MultiDiGraph()
    # for node in graph:
    #     G.add_node(node)
    #     for departure_time, neighbor, arrival_time, identifier in graph[node]:
    #         G.add_edge(node, neighbor, identifier=identifier, departure_time=departure_time, arrival_time=arrival_time)
    #
    # # Adjust layout for better visualization
    # pos = stops_map
    # fig, ax = plt.subplots(figsize=(10, 8))  # Adjust figure size
    # # _draw_labeled_multigraph_v2(G, "identifier", pos, ax=ax)
    # # plt.show()
    #
