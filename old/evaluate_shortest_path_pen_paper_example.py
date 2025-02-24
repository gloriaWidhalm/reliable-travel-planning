# This file contains code to run the simple Dijsktra pathfinder
from old.main import print_path
from constants import LOG_LEVEL
from algorithm.graph import Graph
from algorithm.reliability import compute_reliability

import logging

logging.basicConfig(level=LOG_LEVEL)


def get_graph_data():
    """
    Get the graph data
    @todo this is just a placeholder for now, replace this with the actual function
    """
    # Data structure (tuples sorted by departure time for faster access)
    # We have a dictionary with the nodes as keys and the values are an array with tuples (departure_time, neighbor, arrival_time, trip identifier)
    # times in minutes

    # this is intermediate data to test the algorithm
    graph = {
        # departure node with list of trips (departure nodes in the dictionary to be able to access the data easily)
        # "from" is just additional to be accessible anywhere
        # actual_times is a list of tuples with the actual departure and arrival times
        "Liestal": [
            {
                "from": "Liestal",
                "to": "Olten",
                "planned_departure": 487,
                "planned_arrival": 505,
                "trip_id": "IC6",
                "actual_times": [(487, 505), (490, 508)],
            }
        ],
        "Olten": [
            {
                "from": "Olten",
                "to": "Bern",
                "planned_departure": 509,
                "planned_arrival": 536,
                "trip_id": "IC6",
                "actual_times": [(509, 536), (512, 539)],
            },
            {
                "from": "Olten",
                "to": "Bern",
                "planned_departure": 451,
                "planned_arrival": 478,
                "trip_id": "IC8",
                "actual_times": [(451, 478), (454, 481)],
            },
        ],
        "Bern": [
            {
                "from": "Bern",
                "to": "Thun",
                "planned_departure": 547,
                "planned_arrival": 565,
                "trip_id": "IC6",
                "actual_times": [(547, 565), (550, 568)],
            },
            {
                "from": "Bern",
                "to": "Thun",
                "planned_departure": 487,
                "planned_arrival": 505,
                "trip_id": "IC8",
                "actual_times": [(487, 505), (490, 508)],
            },
        ],
        "Thun": [
            {
                "from": "Thun",
                "to": "Spiez",
                "planned_departure": 566,
                "planned_arrival": 576,
                "trip_id": "IC6",
                "actual_times": [(566, 576), (569, 579)],
            },
            {
                "from": "Thun",
                "to": "Spiez",
                "planned_departure": 506,
                "planned_arrival": 516,
                "trip_id": "IC8",
                "actual_times": [(506, 516), (509, 519)],
            },
        ],
        "Spiez": [
            {
                "from": "Spiez",
                "to": "Visp",
                "planned_departure": 576,
                "planned_arrival": 602,
                "trip_id": "IC6",
                "actual_times": [(576, 602), (579, 605)],
            },
            {
                "from": "Spiez",
                "to": "Visp",
                "planned_departure": 516,
                "planned_arrival": 542,
                "trip_id": "IC8",
                "actual_times": [(516, 542), (519, 545)],
            },
        ],
        "Visp": [
            {
                "from": "Visp",
                "to": "Brig",
                "planned_departure": 603,
                "planned_arrival": 611,
                "trip_id": "IC6",
                "actual_times": [(603, 611), (606, 614)],
            },
            {
                "from": "Visp",
                "to": "Brig",
                "planned_departure": 543,
                "planned_arrival": 551,
                "trip_id": "IC8",
                "actual_times": [(543, 551), (546, 554)],
            },
        ],
        "Brig": [],
        "Aarau": [
            {
                "from": "Aarau",
                "to": "Olten",
                "planned_departure": 438,
                "planned_arrival": 447,
                "trip_id": "IC8",
                "actual_times": [(438, 447), (441, 450)],
            }
        ],
        "Zürich HB": [
            {
                "from": "Zürich HB",
                "to": "Aarau",
                "planned_departure": 404,
                "planned_arrival": 436,
                "trip_id": "IC8",
                "actual_times": [(404, 436), (407, 439)],
            }
        ],
    }

    # even more simple graph for testing
    graph = {
        "Zurich": [
            {
                "from": "Zurich",
                "planned_departure": 5,
                "to": "Olten",
                "planned_arrival": 15,
                "trip_id": "T1",
                "actual_times": [(5, 15), (6, 15), (10, 20)],
            }
        ],
        "Olten": [
            {
                "from": "Olten",
                "planned_departure": 20,
                "to": "Bern",
                "planned_arrival": 30,
                "trip_id": "T2",
                "actual_times": [(20, 30), (20, 32), (25, 35)],
            }
        ],
        "Bern": [
            {
                "from": "Bern",
                "planned_departure": 35,
                "to": "Brig",
                "planned_arrival": 45,
                "trip_id": "T3",
                "actual_times": [(35, 45), (37, 47), (40, 50)],
            }
        ],
        "Brig": [
            {
                "from": "Brig",
                "planned_departure": 55,
                "to": "Milan",
                "planned_arrival": 65,
                "trip_id": "T4",
                "actual_times": [(55, 65), (57, 67), (60, 70)],
            }
        ],
    }

    return graph


if __name__ == "__main__":
    # Code to evaluate different shortest paths

    # get data @todo only a placeholder for now
    graph = get_graph_data()

    # idea: could define a list of start node, start time and destination node and loop over it, then save the results in a pandas dataframe and export it to a csv file (for further analysis)

    # initialize graph G (with graph class)
    G = Graph(graph=graph)

    # Example: shortest path from Bern to Brig
    start_time = 0
    start = "Zurich"
    destination = "Brig"
    shortest_time, shortest_path = G.dijkstra(start, destination, start_time)
    print(
        "We go from",
        start,
        "to",
        destination,
        "starting at",
        start_time,
        "earliest possible arrival",
        shortest_time,
    )
    print_path(shortest_path, start, start_time)
    #
    #
    # evaluate reliability of the path
    time_budget = (
        shortest_time - start_time
    ) * 1  # for the shortest path, we have 100% (and not more) of the time budget
    # # compute the reliability of the path
    shortest_path_reliability = compute_reliability(
        shortest_path, start_time, time_budget, transfer_time=5
    )
    print(
        f"Reliability of the shortest path: {round(shortest_path_reliability * 100, 2)}%"
    )

    # Note: Here, the reliability is based on time budget 1 (which means that the path is reliable if it is completed within the time budget, which is the earliest possible
    # arrival) Therefore, it is only ~10% If we set the time budget a bit higher, the two other trips are also considered (arrive within time budget) and the reliability
    # increases to ~ 62% as in the pen and paper example

    increased_time_budget = time_budget * 2
    shortest_path_reliability = compute_reliability(
        shortest_path, start_time, increased_time_budget, transfer_time=5
    )
    print(
        f"Reliability as in pen & paper example (slightly increased time budget {increased_time_budget}): {round(shortest_path_reliability * 100, 2)}%"
    )
