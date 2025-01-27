import heapq

# Step 0: Define a toy timetable graph
graph = {
    'Liestal': [(487, 'Olten', 505, 'IC6')],
    'Basel SBB': [(475, 'Liestal', 486, 'IC6')],
    'Olten': [(509, 'Bern', 536, 'IC6'), (451, 'Bern', 478, 'IC8')],
    'Bern': [(547, 'Thun', 565, 'IC6'), (487, 'Thun', 505, 'IC8')],
    'Thun': [(566, 'Spiez', 576, 'IC6'), (506, 'Spiez', 516, 'IC8')],
    'Spiez': [(576, 'Visp', 602, 'IC6'), (516, 'Visp', 542, 'IC8')],
    'Visp': [(603, 'Brig', 611, 'IC6'), (543, 'Brig', 551, 'IC8')],
    'Brig': [],
    'Aarau': [(438, 'Olten', 447, 'IC8')],
    'Zürich HB': [(404, 'Aarau', 436, 'IC8')],
}

new_connections = [
    ("Zürich HB", 520, "Winterthur", 550, "IC1"),
    ("Winterthur", 560, "St. Gallen", 620, "IC3"),
    ("St. Gallen", 630, "Chur", 700, "IC2"),
    ("Chur", 710, "Lugano", 760, "IR"),
    ("Lugano", 770, "Milano", 820, "EC"),
    ("Milano", 830, "Venice", 1000, "ES"),
    ("Venice", 1010, "Rome", 1220, "ES"),
    ("Rome", 1230, "Naples", 1320, "IC"),
    ("Naples", 1330, "Salerno", 1400, "RE"),
    ("Basel SBB", 600, "Strasbourg", 660, "ICE"),
    ("Strasbourg", 670, "Paris", 830, "TGV"),
    ("Zürich HB", 700, "Stuttgart", 850, "IC"),
    ("Stuttgart", 900, "Munich", 1020, "IC"),
    ("Munich", 1030, "Salzburg", 1120, "EC"),
]

# Update the graph with new connections
for station, dep, dest, arr, train_id in new_connections:
    if station not in graph:
        graph[station] = []
    graph[station].append((dep, dest, arr, train_id))
    if dest not in graph:
        graph[dest] = []

# -----------------------------------------------------------------------------
# 1. Simple importance measure (e.g. by node degree)
#    In real CH, you consider the # of shortcuts, edge difference, etc.
# -----------------------------------------------------------------------------
def calculate_node_importance(g):
    return {node: len(g[node]) for node in g}

# -----------------------------------------------------------------------------
# 2. Build (prototype) Contraction Hierarchy
#    - Sort nodes by importance
#    - Contract each node in ascending order, adding shortcuts between neighbors
#    - Mark the node as contracted
#    - (In a real CH, you'd store "upward" and "downward" edges separately;
#       here we keep a single adjacency list and highlight the marking step.)
# -----------------------------------------------------------------------------
def build_contraction_hierarchy(original_graph):
    # (a) Copy the original graph so we can augment it with shortcuts
    ch_graph = {node: list(edges) for node, edges in original_graph.items()}

    # (b) Sort nodes by importance
    importance = calculate_node_importance(ch_graph)
    nodes_ordered = sorted(importance.keys(), key=lambda n: importance[n])

    # (c) A dict to keep track of "contracted" status
    contracted = {node: False for node in ch_graph}

    # (d) Contract each node in ascending order
    for node in nodes_ordered:
        # We'll retrieve all current edges from 'node'
        # Each edge looks like (dep_time, neighbor, arr_time, train)
        neighbors = ch_graph[node]

        # Find pairs of neighbors to add shortcuts
        for i in range(len(neighbors)):
            dep_i, neigh_i, arr_i, tr_i = neighbors[i]
            # Skip if neighbor is already contracted in a real advanced CH
            if contracted.get(neigh_i, False):
                continue

            for j in range(i + 1, len(neighbors)):
                dep_j, neigh_j, arr_j, tr_j = neighbors[j]
                if contracted.get(neigh_j, False):
                    continue
                if neigh_i == neigh_j:
                    continue

                # Calculate a possible "shortcut cost" if traveling neigh_i -> node -> neigh_j
                cost_ij = (arr_i - dep_i) + (arr_j - dep_j)

                # We'll define the departure time for the new edge from neigh_i
                # so that effectively you arrive at 'node' at arr_i, then "depart"
                # node at the same time (if zero waiting).  For simplicity, we say:
                shortcut_dep = arr_i
                shortcut_arr = arr_i + cost_ij  # arrival at neigh_j

                # Add a "shortcut" edge to ch_graph[neigh_i]
                ch_graph[neigh_i].append((shortcut_dep, neigh_j, shortcut_arr, "shortcut"))

                # Optionally add the reverse shortcut if your graph is undirected or you need both directions
                cost_ji = (arr_j - dep_j) + (arr_i - dep_i)
                shortcut_dep_rev = arr_j
                shortcut_arr_rev = arr_j + cost_ji
                ch_graph[neigh_j].append((shortcut_dep_rev, neigh_i, shortcut_arr_rev, "shortcut"))

        # ----------------------
        # Mark this node as contracted
        # In a *real* CH, you'd also remove edges leading to or from 'node'
        # if they connect lower->higher in the hierarchy, or keep them in a special
        # "downward" adjacency. We'll skip removing anything in this demo.
        # ----------------------
        contracted[node] = True

        # Real CH might do:
        #   - Move edges from node to a "downEdges" structure if node has higher rank,
        #     or keep them as "upEdges" if node has lower rank, etc.
        #   - Filter out redundant edges.
        # Here we do not remove or filter to keep it simpler.

    return ch_graph, contracted

# -----------------------------------------------------------------------------
# 3. Query: Dijkstra on the augmented CH graph
#    - Because we never fully remove nodes, a standard Dijkstra will still work.
#    - For large graphs, real CH queries do special “upward-downward” searches.
# -----------------------------------------------------------------------------
def query_shortest_path(ch_graph, start, end, start_time):
    # Priority queue: (current_time, current_node)
    pq = [(start_time, start)]
    visited = set()
    best_arrival = {n: float("inf") for n in ch_graph}
    best_arrival[start] = start_time

    while pq:
        current_time, current_node = heapq.heappop(pq)
        if current_node in visited:
            continue
        visited.add(current_node)

        if current_node == end:
            return current_time

        # Explore edges
        for dep_time, neighbor, arr_time, _ in ch_graph[current_node]:
            # We can only board if dep_time >= current_time
            if dep_time >= current_time:
                travel = (arr_time - dep_time)
                arrival = current_time + travel
                if arrival < best_arrival[neighbor]:
                    best_arrival[neighbor] = arrival
                    heapq.heappush(pq, (arrival, neighbor))

    return float("inf")  # no path

# -----------------------------------------------------------------------------
# 4. Demo usage
# -----------------------------------------------------------------------------
def print_graph(title, g, max_edges=15):
    print(f"\n{title}")
    for node, edges in g.items():
        print(f"  {node}:")
        # Just show up to `max_edges` to avoid giant prints
        for e in edges[:max_edges]:
            print(f"    {e}")
        if len(edges) > max_edges:
            print(f"    ...({len(edges)} edges total)")

print_graph("Original Graph", graph)

# Build the CH
ch_graph, contracted_dict = build_contraction_hierarchy(graph)
print_graph("Augmented CH Graph (with shortcuts)", ch_graph, max_edges=10)

# Show which nodes are marked contracted
print("\nContracted Status:")
for station, is_contracted in contracted_dict.items():
    print(f"  {station}: {is_contracted}")

# Query a route in the new CH graph
start_station = "Zürich HB"
end_station   = "Brig"
depart_time   = 400  # 4:00 AM

best_time = query_shortest_path(ch_graph, start_station, end_station, depart_time)
print(f"\nEarliest arrival from {start_station} to {end_station} if leaving at {depart_time}: {best_time}")

earliest_arrival_org = query_shortest_path(graph, start_station, end_station, depart_time)
print(f"\nEarliest arrival time from {start_station} to {end_station} after {depart_time}, original graph: {earliest_arrival_org}")
