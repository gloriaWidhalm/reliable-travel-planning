# This files contains a graph class with graph-related properties and methods.
# It is an abstraction and just easier to work with than a dictionary.
# A baseline for this class is this tutorial: https://www.datacamp.com/tutorial/dijkstra-algorithm-in-python

# The heap queue is a regular heap data structure, where the smallest element is always popped first. (for us with the smallest distance)
from heapq import heapify, heappop, heappush


# Maybe this is redundant, and we want to use networkx instead!


class Graph:
    def __init__(self, graph=None):
        if graph is None:
            graph = {}
        self.graph = graph

    def add_node(self, node):
        """
        Add a node to the graph
        """
        if node not in self.graph:
            self.graph[node] = {}

    def add_edge(self, node1, node2, weight):
        """
        Add an edge between node1 and node2 with a given weight
        """
        if node1 not in self.graph:
            self.add_node(node1)
        if node2 not in self.graph:
            self.add_node(node2)
        self.graph[node1][node2] = weight

    def get_shortest_distances(self, source: str):
        """
        Compute the shortest distances from the source node to all other nodes in the graph
        """
        # initialize distances with infinity
        distances = {node: float("inf") for node in self.graph}
        # for the source node, the distance is 0
        distances[source] = 0
        # set of visited nodes
        visited = set()

        # we want to use the concept of a priority queue, the node with the highest priority is the one with the smallest distance
        # the smallest distance can also be seen as the cost/time/reliability-weighted time to reach a node
        priority_queue = [(0, source)]
        heapify(
            priority_queue
        )  # heapify the list to maintain the heap property (priority queue)

        # we loop over the priority queue until it is empty
        while priority_queue:
            # get the node with the smallest distance (highest priority)
            current_distance, current_node = heappop(priority_queue)

            # check if the current node has been visited -> if yes, skip that node
            if current_node in visited:
                continue
            # otherwise we add it to visited
            visited.add(current_node)

            # now we have to go through all neighbors of our current node
            for neighbor, weight in self.graph[current_node].items():
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

    def shortest_path(self, source: str, target: str):
        """
        Compute the shortest path between any source and target node
        """
        # get predecessors
        _, predecessors = self.get_shortest_distances(source)

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
        return path
