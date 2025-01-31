# This file contains functions that are used in multiple files, and it is more convenient to have them in a separate file.
import logging

from constants import LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL)
from retrieve_data.Network import get_data, process_route_data


def is_transfer_needed(trip_identifier_1: str | None, trip_identifier_2: str | None) -> bool:
    """
    Check if a transfer is needed between two trips. If the trip identifiers are different, a transfer is needed.
    Otherwise, we assume we are in the same train and no transfer is needed.
    """
    # check if the trip identifiers are different
    if trip_identifier_1 and trip_identifier_2 and trip_identifier_1 != trip_identifier_2:
        return True
    return False

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
    #train_data = get_data(desired_date, database_path=data_path)
    train_data = get_data()
    logging.info(f"Data loaded for {desired_date} {train_data.head()}")

    # get graph structure from train data
    return process_route_data(train_data, start_time, end_time, start_station)

def print_path(path, start_node, start_time=0):
    """
    Print the path in a human-readable way
    :param path: tuple with the path (departure_time, node, arrival_time, identifier)
    """
    # The first edge is the source node
    if path is None:
        print("No path found")
        return
    print(f"Start at {start_node} at {start_time}")
    for trip in path:
        departure_time = trip["planned_departure"]
        arrival_time = trip["planned_arrival"]
        node = trip["to"]
        identifier = trip["trip_id"]
        print(f"Take {identifier} to {node} at {departure_time} and arrive at {arrival_time}")