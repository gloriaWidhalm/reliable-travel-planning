# This file contains code to run the simple Dijsktra pathfinder
from graph import Graph
from reliability_v2 import compute_reliability


def print_path(path, start_node, start_time=0):
    """
    Print the path in a human-readable way
    :param path: tuple with the path (departure_time, node, arrival_time, identifier)
    """
    # The first edge is the source node
    print(f"Start at {start_node} at {start_time}")
    for trip in path:
        departure_time = trip["planned_departure"]
        arrival_time = trip["planned_arrival"]
        node = trip["to"]
        identifier = trip["trip_id"]
        print(f"Take {identifier} to {node} at {departure_time} and arrive at {arrival_time}")


# Data structure (tuples sorted by departure time for faster access)
# We have a dictionary with the nodes as keys and the values are an array with tuples (departure_time, neighbor, arrival_time, trip identifier)
# times in minutes

# this is intermediate data to test the algorithm
graph = {
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


if __name__ == "__main__":
    # Code for testing reliability, most reliable path, etc.
    # initialize graph G (with graph class)
    G = Graph(graph=graph)

    # Example: shortest path from Bern to Brig
    start_time = 400
    start = "Bern"
    destination = "Brig"
    shortest_time, shortest_path = G.dijkstra(start, destination, start_time)
    # print(f"Earliest arrival time from Bern to Brig is {shortest_time}")
    # print_path(shortest_path, "Bern", 400)
    # print("Shortest path:", shortest_path)
    #
    #
    # # evaluate reliability of the path
    time_budget = (shortest_time - start_time) * 1.5 # for the shortest path, we have 100% (and not more) of the time budget
    # # compute the reliability of the path
    #shortest_path_reliability = compute_reliability(shortest_path, start_time, time_budget, transfer_time=5)
    #print(f"Reliability of the shortest path: ~{round(shortest_path_reliability*100)}%")

    # Test finding the most reliable path
    reliable_arrival_time, reliability, most_reliable_path = G.find_most_reliable_path(start, destination, start_time, int(time_budget))
    print("We go from", start, "to", destination, "starting at", start_time, "with a time budget of", time_budget, "earliest possible arrival", shortest_time, "latest possible arrival", start_time + time_budget)
    print("Reliability:", reliability, "arrival time with most reliable path", reliable_arrival_time)
    print_path(most_reliable_path, start, start_time)