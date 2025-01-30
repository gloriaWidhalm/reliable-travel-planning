# This file contains code to run the simple Dijsktra pathfinder
from algorithm.main import print_path
from constants import LOG_LEVEL
from graph import Graph
from reliability_v2 import compute_reliability

import logging

from retrieve_data.Network import get_data, process_route_data

logging.basicConfig(level=LOG_LEVEL)

def get_graph_data(desired_date, data_path, start_time, end_time, start_station, use_example_data=False):
    """
    Get the graph data
    """
    # Data structure (tuples sorted by departure time for faster access)
    # We have a dictionary with the nodes as keys and the values are an array with tuples (departure_time, neighbor, arrival_time, trip identifier)
    # times in minutes

    # This is only for quick testing
    if use_example_data:
        # this is intermediate data to test the algorithm
        graph = {
            # departure node with list of trips (departure nodes in the dictionary to be able to access the data easily)
            # "from" is just additional to be accessible anywhere
            # actual_times is a list of tuples with the actual departure and arrival times
            'Liestal': [
                {"from": 'Liestal', "to": 'Olten', "planned_departure": 487, "planned_arrival": 505, "trip_id": 'IC6', "actual_times": [(487, 505), (490, 508)]}
            ],
            'Olten': [
                {"from": 'Olten', "to": 'Bern', "planned_departure": 509, "planned_arrival": 536, "trip_id": 'IC6', "actual_times": [(509, 536), (512, 539)]},
                {"from": 'Olten', "to": 'Bern', "planned_departure": 451, "planned_arrival": 478, "trip_id": 'IC8', "actual_times": [(451, 478), (454, 481)]}
            ],
            'Bern': [
                {"from": 'Bern', "to": 'Thun', "planned_departure": 547, "planned_arrival": 565, "trip_id": 'IC6', "actual_times": [(547, 565), (550, 568)]},
                {"from": 'Bern', "to": 'Thun', "planned_departure": 487, "planned_arrival": 505, "trip_id": 'IC8', "actual_times": [(487, 505), (490, 508)]}
            ],
            'Thun': [
                {"from": 'Thun', "to": 'Spiez', "planned_departure": 566, "planned_arrival": 576, "trip_id": 'IC6', "actual_times": [(566, 576), (569, 579)]},
                {"from": 'Thun', "to": 'Spiez', "planned_departure": 506, "planned_arrival": 516, "trip_id": 'IC8', "actual_times": [(506, 516), (509, 519)]}
            ],
            'Spiez': [
                {"from": 'Spiez', "to": 'Visp', "planned_departure": 576, "planned_arrival": 602, "trip_id": 'IC6', "actual_times": [(576, 602), (579, 605)]},
                {"from": 'Spiez', "to": 'Visp', "planned_departure": 516, "planned_arrival": 542, "trip_id": 'IC8', "actual_times": [(516, 542), (519, 545)]}
            ],
            'Visp': [
                {"from": 'Visp', "to": 'Brig', "planned_departure": 603, "planned_arrival": 611, "trip_id": 'IC6', "actual_times": [(603, 611), (606, 614)]},
                {"from": 'Visp', "to": 'Brig', "planned_departure": 543, "planned_arrival": 551, "trip_id": 'IC8', "actual_times": [(543, 551), (546, 554)]}
            ],
            'Brig': [],
            'Aarau': [
                {"from": 'Aarau', "to": 'Olten', "planned_departure": 438, "planned_arrival": 447, "trip_id": 'IC8', "actual_times": [(438, 447), (441, 450)]}
            ],
            'Zürich HB': [
                {"from": 'Zürich HB', "to": 'Aarau', "planned_departure": 404, "planned_arrival": 436, "trip_id": 'IC8', "actual_times": [(404, 436), (407, 439)]}
            ]
        }
        return graph

    # if the transport_data.db is in a different location, you can specify the path here
    # Also, here you can specify the date of interest
    train_data = get_data(desired_date, database_path=data_path)

    # get graph structure from train data
    graph = process_route_data(train_data, start_time, end_time, start_station)

    return graph


if __name__ == "__main__":
    # Code to evaluate different shortest paths

    start_time = 0 # 0 minutes, please set this to what you need
    end_time = 1440 # 24 hours, please set this to what you need


    # you need to enter stations with their identifier, names are not supported
    # here are some examples, under "OPUIC" you can find the station identifier: https://data.sbb.ch/explore/dataset/stadtefahrplan/table/ (please without commas)
    # or just query the database
    logging.info("Loading graph data")
    # please enter as string, otherwise it will not work
    start = "8507000"  # Bern
    destination = "8501008" # Genève

    # get data
    graph = get_graph_data("2024-10-02", "../transport_data.db", start_time, end_time, start, use_example_data=False)
    logging.info("Graph data loaded")

    # idea: could define a list of start node, start time and destination node and loop over it, then save the results in a pandas dataframe and export it to a csv file (for further analysis)

    # initialize graph G (with graph class)
    G = Graph(graph=graph)

    #logging.debug("Graph: ")
    #logging.debug(G.graph)

    exit(0)

    shortest_time, shortest_path = G.dijkstra(start, destination, start_time)
    print("We go from", start, "to", destination, "starting at", start_time, "earliest possible arrival", shortest_time)
    print_path(shortest_path, start, start_time)
    #
    #
    # evaluate reliability of the path
    time_budget = (shortest_time - start_time) * 1  # for the shortest path, we have 100% (and not more) of the time budget
    # # compute the reliability of the path
    shortest_path_reliability = compute_reliability(shortest_path, start_time, time_budget, transfer_time=5)
    print(f"Reliability of the shortest path: {round(shortest_path_reliability * 100, 2)}%")
