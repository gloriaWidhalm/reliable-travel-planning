# This files contains a graph class with graph-related properties and methods.
# It is an abstraction and just easier to work with than a dictionary.
# A baseline for this class is this tutorial: https://www.datacamp.com/tutorial/dijkstra-algorithm-in-python

# Also, the dijkstra algorithm is based on a ChatGPT chat (2024-11-20): https://chatgpt.com/c/673cb220-5308-8013-bf0d-36f55f78e707

# The heap queue is a regular heap data structure, where the smallest element is always popped first. (for us with the smallest distance)
from heapq import heapify, heappop, heappush


# Maybe this is redundant, and we want to use networkx instead!

# We assume we have a network (graph) with nodes representing locations/stations and multiple edges representing connections between the nodes (with departure and arrival times in minutes)

class Graph:
    def __init__(self, graph=None):
        if graph is None:
            graph = {}
        self.graph = graph
        # sort the connections by departure time
        self.sort_connections()

    def add_node(self, node):
        """
        Add a node to the graph
        """
        if node not in self.graph:
            self.graph[node] = {}

    def add_edge(self, node1, node2, identifier, departure_time, arrival_time):
        """
        Add an edge between node1 and node2 with departure and arrival time
        The edge is represented as a dictionary with the identifier, departure time, and arrival time.
        The identifier is an identifier for the connection (maybe a train number or similar) @TODO -> maybe refine this
        """
        if node1 not in self.graph:
            self.add_node(node1)
        if node2 not in self.graph:
            self.add_node(node2)
        self.graph[node1][node2] = {"identifier": identifier, "departure_time": departure_time, "arrival_time": arrival_time}

    def sort_connections(self):
        """
        Sort the connections of the graph dictionary by departure time
        """
        # go through all nodes in the graph
        for node in self.graph:
            # go through all neighbors of the node
            for neighbor in self.graph[node]:
                # sort the edges by departure time
                self.graph[node][neighbor].sort(key=lambda x: x["departure_time"])

    def dijkstra(self, source: str, target: str, start_time: int):
        """
        Compute the shortest path between any source and target node based on the Dijkstra algorithm
        @param source: the source node
        @param target: the target node
        @param start_time: the start time in minutes
        """
        # initialize the distances (= travel times) with infinity
        distances = {node: float('inf') for node in self.graph}
        # for the source node, the distance is the start time
        distances[source] = start_time
        # initialize our priority queue with the source node and the start time
        priority_queue = [(0, source, start_time)]
        # parent dictionary to store the predecessors of each node (needed to reconstruct the path)
        predecessors = {node: None for node in self.graph}
        # track which edges are taken in the shortest path (since we have multiple edges (=connections) between nodes) -> we need to store the edge information
        edge_taken = {}

        # heapify the priority queue to maintain the heap property
        heapify(priority_queue)

        # loop over the priority queue until it is empty
        while priority_queue:
            # get the node with the smallest distance (highest priority)
            current_distance, current_node, current_time = heappop(priority_queue)

            # check if we have reached the destination (= target node)
            if current_node == target:
                break

            # go through all neighbors of the current node
            for neighbor in self.graph[current_node]:
                # go through all edges/connections between the current node and the neighbor
                for edge in self.graph[current_node][neighbor]:
                    # Check if we can use the edge (connection) -> the departure time of the edge has to be greater than the current time
                    if edge["departure_time"] >= current_time:
                        # calculate the weight of the edge (time to travel from current node to neighbor)
                        weight = edge["arrival_time"] - edge["departure_time"]

                        # @TODO: currently we assume no transfer time / waiting time at the station
                        # @TODO: we must also differentiate between being in the same train (no transfer time) and changing trains (transfer time
                        #  #@TODO -> because each edge is between two nodes (= stops/stations)
                        # calculate the distance to the neighbor node
                        new_distance_neighbor = current_distance + weight

                        # @TODO: add a preference for earlier connections -> if we have multiple connections between two nodes, we want to prefer the earlier one
                        # @TODO: check if the shortest path is the one with the least travel time or the one with the least waiting time
                        # @TOOD -> since we now sort by departure time, we should always take the earliest connection, but if the later connection is faster, now we would take the later one, even if it is much later
                        # check if the new distance is smaller than the existing distance to the neighbor
                        if new_distance_neighbor < distances[neighbor]:
                            # update the distance to the neighbor
                            distances[neighbor] = new_distance_neighbor
                            # add the neighbor to the priority queue
                            heappush(priority_queue, (new_distance_neighbor, neighbor, edge["arrival_time"]))
                            # update the predecessor of the neighbor
                            predecessors[neighbor] = current_node
                            # update the edge taken in the shortest path
                            edge_taken[neighbor] = edge["identifier"]

        print("predecessors", predecessors)
        # reconstruct the shortest path
        path = []
        current_node = target
        while current_node != source:
            path.append(current_node)
            current_node = predecessors[current_node]
        path.append(source)
        # reverse the path to get the correct order (from source to target)
        path.reverse()

        # @TODO: we also want to return the edge taken in the shortest path -> can we incorporate this in the predecessors dictionary?
        # @TODO: how to return the list of used stops/stations in the shortest path between source and target?
        return distances[target], path, edge_taken

    def get_shortest_distances(self, source: str, start_time: int):
        """
        Compute the shortest distances (= travel times) from the source node to all other nodes in the graph
        """
        # initialize distances with infinity
        distances = {node: float('inf') for node in self.graph}
        # for the source node, the distance is the start time
        distances[source] = start_time
        # set of visited nodes
        visited = set()

        # we want to use the concept of a priority queue, the node with the highest priority is the one with the smallest distance
        # the smallest distance can also be seen as the cost/time/reliability-weighted time to reach a node
        priority_queue = [(0, source, start_time)]
        heapify(priority_queue)  # heapify the list to maintain the heap property (priority queue)

        # we loop over the priority queue until it is empty
        while priority_queue:
            # get the node with the smallest distance (highest priority)
            current_distance, current_node, current_time = heappop(priority_queue)

            # check if the current node has been visited -> if yes, skip that node
            # @TODO -> check if we want to combine the shortest path function with the get_shortest_distances function -> to have the dijkstra algorithm in one function
            # @TODO -> probably good idea since we do not have to loop through the graph twice for the predecessors
            # @TODO -> check if we want to add a condition to stop the algorithm if we reach the target node
            # @TODO -> we also need to check which edges are taken -> therefore visited does not work -> we need to add a list of visited edges
            if current_node in visited:
                continue
            # otherwise we add it to visited
            visited.add(current_node)

            # now we have to go through all neighbors of our current node
            for neighbor in self.graph[current_node].items():
                # calculate the weight of the edge (time to travel from current node to neighbor)

                # go through all connections between the current node and the neighbor
                for connection in self.graph[current_node][neighbor]:
                    # calculate the weight of the edge (time to travel from current node to neighbor)
                    weight = connection["arrival_time"] - connection["departure_time"]

                    # and calculate the distance to the other nodes
                    new_distance_neighbor = current_distance + weight
                    # now we have to check if this (new) neighbor distance is smaller than the existing distance to the neighbor
                    if new_distance_neighbor < distances[neighbor]:
                        # overwrite the distance if it is smaller than the existing distance to the neighbor
                        distances[neighbor] = new_distance_neighbor
                        # add it to the queue
                        heappush(priority_queue, (new_distance_neighbor, neighbor))

        # Now we also want to construct the shortest path, not only the distances to each node from the source node
        predecessors = {node: None for node in self.graph}

        # loop through the distances and set the predecessors
        for node, distance in distances.items():
            # go through the neighbors to compare the distance and weights
            for neighbor, weight in self.graph[node].items():
                # if the distance of the neighbor is the same as the distance + the weight of the neighbor, we add the predecessor
                if distances[neighbor] == distance + weight:
                    predecessors[neighbor] = node

        return distances, predecessors

    def shortest_path(self, source: str, target: str, start_time: int):
        """
        Compute the shortest path between any source and target node
        """
        # get predecessors
        distances, predecessors = self.get_shortest_distances(source, start_time)

        # prepare path list
        path = []

        # generate path by starting from the target node and traversing to the source node
        path.append(target)
        current_node = target
        # we loop until we are at the source node
        while current_node != source:
            for node, predecessor in predecessors.items():
                # if the predecessor is the same as the current node
                if current_node == node:
                    # add predecessor to path
                    path.append(predecessor)
            # set the current node of interest (=last element in path)
            current_node = path[len(path) - 1]

        # reverse path to get correct order
        path.reverse()
        return distances, path
