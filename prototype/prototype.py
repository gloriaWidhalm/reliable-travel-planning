import logging
import time

from constants import LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL)

import duckdb

from algorithm.evaluate_shortest_paths import get_graph_data
from algorithm.graph import Graph
from algorithm.helper import print_path, get_specific_station_identifier_from_name, get_specific_station_name_from_identifier
from algorithm.reliability_v2 import compute_reliability

def setup_network_data(start, destination, start_time, use_example=False):
    if not use_example:
        # get stop ids from names
        start = get_specific_station_identifier_from_name(stop_name=start)
        destination = get_specific_station_identifier_from_name(stop_name=destination)

        # parse to number
        start = int(start)
        destination = int(destination)


    # set end time artificially (only support up to 6 hours)
    end_time = start_time + 120

    run_time_start_generate_graph = time.time()
    # get data
    graph = get_graph_data("2024-10-02", "../transport_data.db", start_time, end_time, start, use_example_data=use_example)
    logging.info("Graph data loaded")

    run_time_end_generate_graph = time.time()
    runtime_generate_graph = run_time_end_generate_graph - run_time_start_generate_graph
    logging.info(f"Runtime for generating graph: {runtime_generate_graph} seconds")

    return graph, start, destination

def run_algorithms(graph, start, destination, start_time, time_budget_multiplier=1.5):
    # initialize graph G (with graph class)
    G = Graph(graph=graph)

    # if the graph is empty, return
    if not G.graph:
        logging.info("Graph is empty")
        return
    run_time_shortest_path_start = time.time()
    # find shortest path
    shortest_time, shortest_path = G.dijkstra(start, destination, start_time)
    run_time_shortest_path_end = time.time()
    runtime_shortest_path = run_time_shortest_path_end - run_time_shortest_path_start

    # check if length of shortest is 0, if so -> no shortest path found
    if len(shortest_path) == 0:
        return {}

    time_budget_shortest_path = (shortest_time - start_time) * 1  # for the shortest path, we have 100% (and not more) of the time budget
    shortest_path_reliability = compute_reliability(shortest_path, start_time, time_budget_shortest_path, transfer_time=5)
    logging.info("Found shortest path")
    print_path(shortest_path, start, start_time, convert_ids_to_names=True)

    # find most reliable path
    time_budget = time_budget_shortest_path * time_budget_multiplier
    run_time_start = time.time()
    reliable_arrival_time, reliability, most_reliable_path = G.find_most_reliable_path(start, destination, start_time, int(time_budget))
    run_time_end = time.time()
    runtime = run_time_end - run_time_start

    return {
        "earliest_arrival_time": shortest_time,
        "shortest_path": shortest_path,
        "shortest_path_reliability": shortest_path_reliability,
        "runtime_shortest_path": runtime_shortest_path,  # in seconds
        "most_reliable_path": most_reliable_path,
        "reliability": reliability,
        "runtime": runtime, # in seconds
        "start_station": start,
        "destination_station": destination
    }


def find_shortest_and_most_reliable_path(start, destination, start_time, time_budget_multiplier=1.5, use_example=False) -> dict:
    """
    Find the shortest and most reliable path from start to destination
    :param start: start station
    :param destination: destination station
    :param start_time: start time
    :param time_budget_multiplier: time budget multiplier
    :return: dictionary with the following keys:
        - earliest_arrival_time: earliest arrival time
        - shortest_path: shortest path
        - shortest_path_reliability: reliability of the shortest path
        - most_reliable_path: most reliable path
        - reliability: reliability of the most reliable path
    """
    logging.info(f"Loading graph data for {start} to {destination}")

    graph, start, destination = setup_network_data(start, destination, start_time, use_example)

    return run_algorithms(graph, start, destination, start_time, time_budget_multiplier)

if __name__ == "__main__":

    start_time = 600  # 10 AM, please set this to what you need

    # you need to enter stations with their identifier, names are not supported
    # here are some examples, under "OPUIC" you can find the station identifier: https://data.sbb.ch/explore/dataset/stadtefahrplan/table/ (please without commas)
    # or just query the database (BPUIC)
    # please enter as string, otherwise it will not work
    start = "Luzern"  #
    destination = "Zug"  #

    #desired_stop_id = 8507000
    #desired_stop_name = "Bern"
    # stop = get_specific_station_identifier_from_name(stop_name="Zürich HB")
    # print(stop)
    # stop_name = get_specific_station_name_from_identifier(stop_id="8501000")
    # print("stop_name", stop_name)

    result = find_shortest_and_most_reliable_path(start, destination, start_time)
    if len(result.values()) == 0:
        logging.info("No solution could be found.")
        exit(0)

    print(result["most_reliable_path"])
    print("** Result **")
    print("Earliest arrival time:", result["earliest_arrival_time"])
    print("Shortest path reliability:", result["shortest_path_reliability"])
    print("Most reliable path reliability:", result["reliability"])
    print("Runtime:", result["runtime"])
    print("Most reliable path route:")
    print_path(result["most_reliable_path"], start_node=result["start_station"], start_time=start_time, convert_ids_to_names=True)

    #print(result)

