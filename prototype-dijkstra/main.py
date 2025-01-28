# This file contains code to run the simple Dijsktra pathfinder
from graph import Graph



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

# this is intermediate data to test the algorithm
graph_dict = {
    # departure node with list of trips (departure nodes in the dictionary to be able to access the data easily)
    # "from" is just additional to be accessible anywhere
    # actual_times is a list of tuples with the actual departure and arrival times
    'Liestal': [
        { "from": 'Liestal', "to": 'Olten', "planned_departure": 487, "planned_arrival": 505, "trip_id": 'IC6', "actual_times": [(487, 505), (490, 508) ] }
    ],
    'Olten': [
        { "from": 'Olten', "to": 'Bern', "planned_departure": 509, "planned_arrival": 536, "trip_id": 'IC6', "actual_times": [(509, 536), (512, 539) ] },
        { "from": 'Olten', "to": 'Bern', "planned_departure": 451, "planned_arrival": 478, "trip_id": 'IC8', "actual_times": [(451, 478), (454, 481) ] }
    ],
    'Bern': [
        { "from": 'Bern', "to": 'Thun', "planned_departure": 547, "planned_arrival": 565, "trip_id": 'IC6', "actual_times": [(547, 565), (550, 568) ] },
        { "from": 'Bern', "to": 'Thun', "planned_departure": 487, "planned_arrival": 505, "trip_id": 'IC8', "actual_times": [(487, 505), (490, 508) ] }
    ],
    'Thun': [
        { "from": 'Thun', "to": 'Spiez', "planned_departure": 566, "planned_arrival": 576, "trip_id": 'IC6', "actual_times": [(566, 576), (569, 579) ] },
        { "from": 'Thun', "to": 'Spiez', "planned_departure": 506, "planned_arrival": 516, "trip_id": 'IC8', "actual_times": [(506, 516), (509, 519) ] }
    ],
    'Spiez': [
        { "from": 'Spiez', "to": 'Visp', "planned_departure": 576, "planned_arrival": 602, "trip_id": 'IC6', "actual_times": [(576, 602), (579, 605) ] },
        { "from": 'Spiez', "to": 'Visp', "planned_departure": 516, "planned_arrival": 542, "trip_id": 'IC8', "actual_times": [(516, 542), (519, 545) ] }
    ],
    'Visp': [
        { "from": 'Visp', "to": 'Brig', "planned_departure": 603, "planned_arrival": 611, "trip_id": 'IC6', "actual_times": [(603, 611), (606, 614) ] },
        { "from": 'Visp', "to": 'Brig', "planned_departure": 543, "planned_arrival": 551, "trip_id": 'IC8', "actual_times": [(543, 551), (546, 554) ] }
    ],
    'Brig': [],
    'Aarau': [
        { "from": 'Aarau', "to": 'Olten', "planned_departure": 438, "planned_arrival": 447, "trip_id": 'IC8', "actual_times": [(438, 447), (441, 450) ] }
    ],
    'Zürich HB': [
        { "from": 'Zürich HB', "to": 'Aarau', "planned_departure": 404, "planned_arrival": 436, "trip_id": 'IC8', "actual_times": [(404, 436), (407, 439) ] }
    ]
}


# initialize graph G (with graph class)
G = Graph(graph=graph_dict)

# Example: shortest path from B to D
shortest_time, shortest_path = G.dijkstra("Bern", "Brig", 400)
print(f"Earliest arrival time from B to D is {shortest_time}")
print_path(shortest_path)
print("Shortest path:", shortest_path)


# get edges that are part of the shortest path
# @TODO fix that -> get the train identifier for the first edge
shortest_path[0] = (shortest_path[0][0], shortest_path[0][1], shortest_path[0][2], shortest_path[1][3])  #
edges_shortest_path = [(shortest_path[i][1], shortest_path[i + 1][1], shortest_path[i][3]) for i in range(len(shortest_path) - 1)]
# get edges that are not part of the shortest path
edges_not_shortest_path = [(node, edge[1], edge[3]) for node in graph for edge in graph[node] if (node, edge[1], edge[3]) not in edges_shortest_path]



