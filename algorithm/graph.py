# This files contains a graph class with graph-related properties and methods.
# It is an abstraction and just easier to work with than a dictionary.
# A baseline for this class is this tutorial: https://www.datacamp.com/tutorial/dijkstra-algorithm-in-python
# Also, the dijkstra algorithm is based on a ChatGPT chat (2024-11-20): https://chatgpt.com/c/673cb220-5308-8013-bf0d-36f55f78e707
# And also the chat on (2024-11-24): https://chatgpt.com/share/67431b48-4a30-8013-9c88-6cc073907030 (adjustments for arrival time and different data structure)
from copy import deepcopy
# The heap queue is a regular heap data structure, where the smallest element is always popped first. (for us with the smallest distance)
from heapq import heapify, heappop, heappush

from algorithm.helper import is_transfer_needed
from algorithm.reliability_v2 import compute_reliability, TRANSFER_TIME_DEFAULT


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

    def add_edge(self, node1, node2, identifier, departure_time, arrival_time, actual_times):
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
        self.graph[node1].append(
            {"from": node1, "to": node2, "planned_departure": departure_time, "planned_arrival": arrival_time, "trip_id": identifier, "actual_times": actual_times})

    def sort_connections(self):
        """
        Sort the connections of the graph dictionary by departure time
        """
        # go through all nodes in the graph
        for node in self.graph:
            # sort the connections of the node by departure time
            self.graph[node].sort(key=lambda x: x["planned_departure"])

    def dijkstra(self, source: str, target: str, start_time: int, transfer_time=TRANSFER_TIME_DEFAULT) -> tuple[int, list[dict]]:
        """
        Compute the shortest path (in terms of earliest arrival time) between any source and target node based on the Dijkstra algorithm
        @param source: the source node
        @param target: the target node
        @param start_time: the start time in minutes
        @param transfer_time: the transfer time in minutes
        """
        # initialize the arrival_times (distances in terms of time) with infinity
        earliest_arrival_times = {node: float('inf') for node in self.graph}
        # for the source node, the distance is the start time
        earliest_arrival_times[source] = start_time
        # initialize our priority queue with the source node and the start time
        priority_queue = [(start_time, source, None, [])]  # (arrival_time, node, train_identifier, actual_times), for the priority queue, a tuple is fine
        # parent dictionary to store the predecessors of each node (needed to reconstruct the path)
        predecessors = {node: None for node in self.graph}

        # heapify the priority queue to maintain the heap property
        heapify(priority_queue)

        # loop over the priority queue until it is empty
        while priority_queue:
            # get the node with the earliest arrival time (highest priority)
            # current_time in a sense of cost
            current_arrival, current_node, current_train_identifier, current_actual_times = heappop(priority_queue)

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
                actual_times = connection["actual_times"]
                # check if we can use the connection -> the departure time of the connection has to be greater than the current time
                if departure_time >= current_arrival:
                    # if we are not in the same train (transfer needed)
                    # check if we can make the connection (meaning current arrival time + transfer time is smaller than the departure time of the connection)
                    if is_transfer_needed(current_train_identifier, train_identifier) and current_arrival + transfer_time >= departure_time:
                        continue

                    # check if the new arrival time is smaller than the existing arrival time to the neighbor
                    # only update if the new arrival time is smaller
                    if neighbor in earliest_arrival_times and arrival_time < earliest_arrival_times[neighbor]:
                        # update the arrival time to the neighbor
                        earliest_arrival_times[neighbor] = arrival_time
                        # add the neighbor to the priority queue
                        heappush(priority_queue, (arrival_time, neighbor, train_identifier, actual_times))
                        # update the predecessor of the neighbor
                        predecessors[neighbor] = (departure_time, current_node, arrival_time, train_identifier, actual_times)

        # reconstruct the shortest path
        path = []
        current_node = target
        while current_node != source:
            # get info from the predecessor
            departure_time, next_node, arrival_time, train_identifier, actual_times = predecessors[current_node]
            # to have the same structure as the graph, only one element in the list
            path.append({"from": next_node, "to": current_node, "planned_departure": departure_time, "planned_arrival": arrival_time, "trip_id": train_identifier,
                                   "actual_times": actual_times})
            current_node = next_node
        # reverse the path to get the correct order (from source to target)
        path.reverse()

        return earliest_arrival_times[target], path

    def find_most_reliable_path(self, source: str, target: str, start_time: int, time_budget: int, transfer_time=TRANSFER_TIME_DEFAULT) -> tuple[int, float, list[dict]]:
        """
        Find the most reliable "itinerary" / path using a network search algorithm, based on the reference paper "The most reliable flight itinerary problem" (Redmond et al., 2019)
        In this context, path, sequence of trips and itinerary means basically the same.
        @:param source: origin of the path
        @:param target: destination of the path
        @:param start_time: start time of considered trips, when we start the "journey"
        """
        # Initialize most reliable path
        most_reliable_path = None
        # Initialize k (used as additional "tiebreaker" for the comparison of the heap queue)
        k = 1
        # Initialize list with partial paths/itineraries (reliability, label k (as additional identifier of the partial path, time between start time and the scheduled arrival
        # of the current tail trip in the itinerary/path, probability of last/tail trip arriving at time t dependent on making the connections, and list of nodes part of the
        # path (node with actual time information))
        priority_queue = [(1, k, 0, None, [{"from": source, "to": source, "actual_times": []}])]
        position_of_trips = 4  # position of the trips in the tuple

        # heapify the priority queue to maintain the heap property (from the initial list)
        heapify(priority_queue)

        # @todo -> not working yet, since we append each connection and the path grows and grows
        #  @todo (but we e.g. append Bern-Thun twice (with different scheduled times) ... why?)
        while priority_queue:
            # get path with the highest reliability from queue
            path_highest_reliability = heappop(priority_queue)
            # get the last (tail) trip from the path with the highest reliability
            last_trip = deepcopy(path_highest_reliability[position_of_trips][-1])  # is the element position of the trips, -1 is the last
            # get all edges/arcs (connections to other stations) that are adjacent (neighbors) to the last trip (e.g., all trips from Bern to somewhere else)
            # first, we need the station (which is the arrival station, or "to")
            last_station = last_trip["to"]
            # then we can use the graph-structure to get all edges (connections) from this node/station
            # @todo: add function that returns only the connections that are after our start time
            possible_connections = self.graph[last_station]  # possible connections = adjacent edges
            # go through all adjacent edges to "build"/extend our path towards our target/destination further
            for connection in possible_connections:
                extended_trips = deepcopy(path_highest_reliability[position_of_trips])  # the trips in the tuple
                extended_trips.append(connection)
                probability_arrival, probability_connection_made = compute_reliability(extended_trips, start_time, time_budget, complete_path=False, transfer_time=transfer_time)

                # adjust the total time (time between start time and the scheduled arrival of the current tail flight in the itinerary/path)
                total_time_between_start_scheduled_arrival = connection["planned_arrival"] - start_time  # @todo, check if this is correct

                # add the connection and the obtained information to the path (since it is a tuple, we need to do it this way)
                extended_path = (probability_connection_made, k, total_time_between_start_scheduled_arrival, probability_arrival, extended_trips)

                # Update k (label for the path)
                k += 1

                # check if we have reached the destination (= target node)
                if connection["to"] == target:
                    # check if the new path is more reliable than the current most reliable path
                    if most_reliable_path is None or probability_arrival > most_reliable_path[0]:
                        most_reliable_path = extended_path
                else:
                    # add the extended path to the priority queue
                    heappush(priority_queue, extended_path)
        # get the arrival time of the most reliable path
        arrival_time = start_time + most_reliable_path[2]
        reliability = most_reliable_path[0]
        most_reliable_path_transformed = most_reliable_path[position_of_trips]
        # remove first element (the source station)
        most_reliable_path_transformed.pop(0)
        return arrival_time, reliability, most_reliable_path_transformed
