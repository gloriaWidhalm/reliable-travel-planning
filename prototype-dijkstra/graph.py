# This files contains a graph class with graph-related properties and methods.
# It is an abstraction and just easier to work with than a dictionary.
# A baseline for this class is this tutorial: https://www.datacamp.com/tutorial/dijkstra-algorithm-in-python

# Also, the dijkstra algorithm is based on a ChatGPT chat (2024-11-20): https://chatgpt.com/c/673cb220-5308-8013-bf0d-36f55f78e707
# And also the chat on (2024-11-24): https://chatgpt.com/share/67431b48-4a30-8013-9c88-6cc073907030 (adjustments for arrival time and different data structure)

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
            self.graph[node] = []

    def add_edge(self, node1, node2, identifier, departure_time, arrival_time):
        """
        Add an edge between node1 and node2 with departure and arrival time, and an identifier
        The edge is represented as a tuple (departure_time, node2, arrival_time, identifier)
        The identifier is an identifier for the connection (maybe a train number or similar) @TODO -> maybe refine this
        """
        if node1 not in self.graph:
            self.add_node(node1)
        if node2 not in self.graph:
            self.add_node(node2)
        # add the connection to the graph
        self.graph[node1].append({"from": node1, "to": node2, "planned_departure": departure_time, "planned_arrival": arrival_time, "trip_id": identifier})

    def sort_connections(self):
        """
        Sort the connections of the graph dictionary by departure time
        """
        # go through all nodes in the graph
        for node in self.graph:
            # sort the connections of the node by departure time
            self.graph[node].sort(key=lambda x: x["planned_departure"])

    def dijkstra(self, source: str, target: str, start_time: int):
        """
        Compute the shortest path (in terms of earliest arrival time) between any source and target node based on the Dijkstra algorithm
        @param source: the source node
        @param target: the target node
        @param start_time: the start time in minutes
        """
        # initialize the arrival_times (distances in terms of time) with infinity
        earliest_arrival_times = {node: float('inf') for node in self.graph}
        # for the source node, the distance is the start time
        earliest_arrival_times[source] = start_time
        # initialize our priority queue with the source node and the start time
        priority_queue = [(start_time, source, 0, None)] # (arrival_time, node, time, train_identifier), for the priority queue, a tuple is fine
        # parent dictionary to store the predecessors of each node (needed to reconstruct the path)
        predecessors = {node: None for node in self.graph}

        # heapify the priority queue to maintain the heap property
        heapify(priority_queue)

        # loop over the priority queue until it is empty
        while priority_queue:
            # get the node with the earliest arrival time (highest priority)
            # current_time in a sense of cost
            current_arrival, current_node, current_time, train_identifier = heappop(priority_queue)

            # check if we have reached the destination (= target node)
            if current_node == target:
                break

            # go through all connections of the current node
            for connection in self.graph[current_node]:
                # get infos from the connection
                departure_time = connection["planned_departure"]
                neighbor = connection["to"]
                arrival_time = connection["planned_arrival"]
                train_identifier = connection["trip_id"]
                # check if we can use the connection -> the departure time of the connection has to be greater than the current time
                if departure_time >= current_time:
                    # calculate the travel time
                    travel_time = arrival_time - departure_time

                    # @TODO: currently we assume no transfer time / waiting time at the station
                    # @TODO: we must also differentiate between being in the same train (no transfer time) and changing trains (transfer time
                    #  #@TODO -> because each edge is between two nodes (= stops/stations)
                    # @TODO -> what is this actually?
                    total_cost = current_arrival + travel_time

                    # check if the new arrival time is smaller than the existing arrival time to the neighbor
                    # only update if the new arrival time is smaller
                    if neighbor in earliest_arrival_times and arrival_time < earliest_arrival_times[neighbor]:
                        # update the arrival time to the neighbor
                        earliest_arrival_times[neighbor] = arrival_time
                        # add the neighbor to the priority queue
                        heappush(priority_queue, (arrival_time, neighbor, total_cost, train_identifier))
                        # update the predecessor of the neighbor
                        predecessors[neighbor] = (departure_time, current_node, arrival_time, train_identifier)

        # reconstruct the shortest path
        path = []
        current_node = target
        while current_node != source:
            # get info from the predecessor
            departure_time, next_node, arrival_time, train_identifier = predecessors[current_node]
            path.append((departure_time, current_node, arrival_time, train_identifier))
            current_node = next_node
        # add the source node to the path
        path.append((start_time, source, start_time, None))
        # reverse the path to get the correct order (from source to target)
        path.reverse()

        return earliest_arrival_times[target], path