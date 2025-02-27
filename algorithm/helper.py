# This file contains functions that are used in multiple files, and it is more convenient to have them in a separate file.
import logging

import duckdb

from constants import LOG_LEVEL
from retrieve_data.Network_wcancelled import get_data, process_route_data

logging.basicConfig(level=LOG_LEVEL)


def is_transfer_needed(
    trip_identifier_1: str | None, trip_identifier_2: str | None
) -> bool:
    """
    Check if a transfer is needed between two trips. If the trip identifiers are different, a transfer is needed.
    Otherwise, we assume we are in the same train and no transfer is needed.
    """
    # check if the trip identifiers are different
    return (
        trip_identifier_1
        and trip_identifier_2
        and trip_identifier_1 != trip_identifier_2
    )


def get_graph_data(
    desired_date, data_path, start_time, end_time, start_station, use_example_data=False
):
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
        return graph

    # if the transport_data.db is in a different location, you can specify the path here
    # Also, here you can specify the date of interest
    # train_data = get_data(desired_date, database_path=data_path)
    train_data = get_data(database_path=data_path)
    logging.info(f"Data loaded for {desired_date}")

    # get graph structure from train data
    return process_route_data(train_data, start_time, end_time, start_station)


def print_path(path, start_node, start_time=0, convert_ids_to_names=False):
    """
    Print the path in a human-readable way
    :param path: tuple with the path (departure_time, node, arrival_time, identifier)
    """
    # The first edge is the source node
    if path is None:
        print("No path found")
        return
    if convert_ids_to_names:
        # check if start node is a string, if yes, skip

        start_station = get_specific_station_name_from_identifier(stop_id=start_node)
        start_node = start_station
    print(f"Start at {start_node} at {start_time}")
    for trip in path:
        departure_time = trip["planned_departure"]
        arrival_time = trip["planned_arrival"]
        node = trip["to"]
        if convert_ids_to_names:
            node = get_specific_station_name_from_identifier(stop_id=node)
        identifier = trip["trip_id"]
        if convert_ids_to_names:
            identifier_id = identifier
            identifier = get_specific_trip_identifier_from_identifier(
                trip_id=identifier
            )
        print(
            f"Take {identifier} to {node} at {departure_time} and arrive at {arrival_time}, (technical identifier: {identifier_id})"
        )


def consolidate_path(path_lst: list[dict]) -> list[dict]:
    """
    Consolidate a list of paths into a single path.
    :param path_lst: list of paths

    :return: consolidated path
    """
    consolidated_path = []

    # dictionary stores:
    # from, to, actual_times, planned departure, planned arrival, trip_id
    if len(path_lst) in (0, 1):
        return path_lst
    current_trip = path_lst[0]

    def _construct_payload(current_trip, next_trip):
        actual_times = merge_actual_times(
            current_trip["actual_times"], next_trip["actual_times"]
        )

        return {
            "from": current_trip["from"],
            "to": next_trip["to"],
            "planned_departure": current_trip["planned_departure"],
            "planned_arrival": next_trip["planned_arrival"],
            "trip_id": current_trip["trip_id"],
            "actual_times": actual_times,
        }

    # Iterate to the last trip_id
    for i in range(1, len(path_lst)):
        if current_trip["trip_id"] != path_lst[i]["trip_id"]:
            j = i - 1

            # Construct the consolidated payload with the previous trip
            payload = _construct_payload(current_trip, path_lst[j])

            # Append it the final list
            consolidated_path.append(payload)

            # Set the current iteration to the current trip
            current_trip = path_lst[i]

    # Edge case => we do not change the trip at all / need to consolidate the last entry as well
    if current_trip["trip_id"] == path_lst[-1]["trip_id"]:
        payload = _construct_payload(current_trip, path_lst[-1])
        consolidated_path.append(payload)

    return consolidated_path


def merge_actual_times(actual_times_first_trip, actual_times_second_trip):
    """
    Merge the actual times from the last trip and the current connection
    Note: This is a simplification, we could use a more advanced (or should in a realistic condition) to properly match the actual times
    Because it could potentially be that we have a different number of actual time observations/historical departure and arrival times
    """

    # get actual times from last trip and current connection, using the departure times from the last trip and the arrival times from the current connection
    actual_times = []
    # Note: this is a simplification (for matching the actual times)
    # get number of historic departure times from the last trip
    number_actual_times_last_trip = len(actual_times_first_trip)
    # get number of historic arrival times from the current connection
    number_actual_times_current_connection = len(actual_times_second_trip)
    # take the minimum of the two
    number_actual_times = min(
        number_actual_times_last_trip, number_actual_times_current_connection
    )
    # now combine the actual times (departure from last trip and arrival from current connection), assuming the order is correct
    for i in range(number_actual_times):
        # add the actual times to the list, this is a simplification
        # (we could do a more sophisticated approach to check for the actual times and also to match them)
        actual_times.append(
            (actual_times_first_trip[i][0], actual_times_second_trip[i][1])
        )
    return actual_times


def get_specific_station_identifier_from_name(db_connection=None, stop_name=None):
    if not db_connection:
        connection = duckdb.connect("../transport_data.db", read_only=True)
    else:
        connection = db_connection
    if stop_name:
        query = f"""SELECT BPUIC, STOP_NAME FROM services WHERE STOP_NAME LIKE '%{stop_name}%' limit 1 """
    # optionally, we could
    # elif stop_id:
    # query = f'''SELECT STOP_NAME FROM services WHERE BPUIC = '{stop_id}' limit 1'''
    df = connection.execute(query).df()
    if df.empty or "BPUIC" not in df.columns:
        return stop_name
    return df["BPUIC"][0]


def get_specific_station_name_from_identifier(db_connection=None, stop_id=None):
    if not db_connection:
        connection = duckdb.connect("../transport_data.db", read_only=True)
    else:
        connection = db_connection
    if stop_id:
        query = f"""SELECT STOP_NAME FROM services WHERE BPUIC = '{stop_id}' limit 1"""
    df = connection.execute(query).df()

    if df.empty or "STOP_NAME" not in df.columns:
        return stop_id
    return df["STOP_NAME"][0]


def get_specific_trip_identifier_from_identifier(db_connection=None, trip_id=None):
    if not db_connection:
        connection = duckdb.connect("../transport_data.db", read_only=True)
    else:
        connection = db_connection
    if trip_id:
        query = f"""SELECT LINE_TEXT FROM services WHERE TRIP_IDENTIFIER = '{trip_id}' limit 1"""
    df = connection.execute(query).df()

    if df.empty or "LINE_TEXT" not in df.columns:
        return (
            trip_id  # return the original trip id if the query did not return anything
        )
    return df["LINE_TEXT"][0]


def get_coordinates_from_station_list(
    db_connection=None, station_list=None, use_stop_name=True
):
    if not db_connection:
        connection = duckdb.connect("../gtfs_train.db", read_only=True)
    else:
        connection = db_connection
    if station_list:
        if use_stop_name:
            query = f"""SELECT stop_id, stop_name, stop_lat, stop_lon FROM stops WHERE stop_name IN {tuple(station_list)}"""
        else:
            query = f"""SELECT stop_id, stop_name, stop_lat, stop_lon FROM stops WHERE stop_id IN {tuple(station_list)}"""
    df = connection.execute(query).df()
    # remove duplicates based on stop_name, lat, lon
    df = df.drop_duplicates(subset=["stop_name", "stop_lat", "stop_lon"])
    return df


def minutes_to_time(minutes):
    """
    Convert minutes to time
    """
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours:02}:{minutes:02}"
