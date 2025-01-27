import heapq

# Note: for better understanding I prompted ChatGPT to generate a simple example of Dijkstra's algorithm with reliability
# This is the solution provided by ChatGPT (and a bit adjusted)

def dijkstra_with_reliability(graph, start, end):
    # Priority queue to store (cost, node)
    pq = [(0, start)]
    # Distances dictionary to track the shortest distances to each node
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    # Parent dictionary to reconstruct the path
    parents = {node: None for node in graph}

    while pq:
        current_distance, current_node = heapq.heappop(pq)

        # If we've reached the destination, stop
        if current_node == end:
            break

        for neighbor, (time, reliability) in graph[current_node]:
            # Calculate reliability-adjusted weight
            adjusted_weight = time / reliability  # Example formula
            distance = current_distance + adjusted_weight
            # If a shorter path is found
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                parents[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))

    # Reconstruct the shortest path
    path = []
    current = end
    while current:
        path.append(current)
        current = parents[current]
    path.reverse()

    return distances[end], path

# Example graph (nodes and edges with weights: time, reliability set to 1 for simplicity)
graph_without_reliability = {
    'A': [('B', (1, 1)), ('C', (4, 1))],
    'B': [('A', (1, 1)), ('C', (2, 1)), ('D', (6, 1))],
    'C': [('A', (4, 1)), ('B', (2, 1)), ('D', (3, 1))],
    'D': [('B', (6, 1)), ('C', (3, 1))]
}

# Test the algorithm without reliability
start_node = 'A'
end_node = 'D'
shortest_distance, shortest_path = dijkstra_with_reliability(graph_without_reliability, start_node, end_node)
print(f"Shortest distance (based on distance/time): {shortest_distance}")
print(f"Shortest path: {shortest_path}")

# Example graph (nodes and edges with weights: (time, reliability))
graph_with_reliability = {
    'A': [('B', (1, 0.9)), ('C', (4, 0.8))],
    'B': [('A', (1, 0.9)), ('C', (2, 0.95)), ('D', (6, 0.6))],
    'C': [('A', (4, 0.8)), ('B', (2, 0.95)), ('D', (3, 0.9))],
    'D': [('B', (6, 0.6)), ('C', (3, 0.9))]
}

# Test the algorithm
start_node = 'A'
end_node = 'D'
shortest_distance, shortest_path = dijkstra_with_reliability(graph_with_reliability, start_node, end_node)
print(f"Shortest distance (reliability-adjusted): {shortest_distance}")
print(f"Shortest path: {shortest_path}")

# ** VISUALIZATION **
# visualize the graph
import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()
for node, edges in graph_with_reliability.items():
    for edge in edges:
        G.add_edge(node, edge[0], weight=edge[1][0]/edge[1][1])

pos = nx.spring_layout(G)
edge_labels = {(u, v): f"{d['weight']}" for u, v, d in G.edges(data=True)}
nx.draw(G, pos, with_labels=True, node_size=2000, node_color='skyblue', font_size=10, font_weight='bold')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
# add a title
plt.title("Simple graph with reliability-adjusted weights (time/reliability)")
plt.show()


# also visualize the shortest path graph with time weights
G_shortest_path = nx.Graph()
for node, edges in graph_with_reliability.items():
    for edge in edges:
        G_shortest_path.add_edge(node, edge[0], weight=edge[1][0])

pos = nx.spring_layout(G_shortest_path)
edge_labels = {(u, v): f"{d['weight']}" for u, v, d in G_shortest_path.edges(data=True)}
nx.draw(G_shortest_path, pos, with_labels=True, node_size=2000, node_color='lightcoral', font_size=10, font_weight='bold')
nx.draw_networkx_edge_labels(G_shortest_path, pos, edge_labels=edge_labels)
# add a title
plt.title("Shortest path in the graph, weights are the time between the nodes")
plt.show()

