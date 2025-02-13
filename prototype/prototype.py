import logging
import time

import duckdb

from algorithm.evaluate_shortest_paths import get_graph_data
from algorithm.graph import Graph
from algorithm.helper import print_path, get_specific_station_identifier_from_name
from algorithm.reliability_v2 import compute_reliability


def find_shortest_and_most_reliable_path(start, destination, start_time, time_budget_multiplier=1.5) -> dict:
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
    # @todo -> could be also directly given the ids, then these functions are not needed
    # get stop ids from names
    start = get_specific_station_identifier_from_name(stop_name=start)
    destination = get_specific_station_identifier_from_name(stop_name=destination)

    # parse to number
    start = int(start)
    destination = int(destination)

    logging.info(f"Loading graph data for {start} to {destination}")

    # set end time artificially (currently only support 3-6 hours, so set it to 5 hours)
    end_time = start_time + 60
    # get data
    graph = get_graph_data("2024-10-02", "../transport_data.db", start_time, end_time, start, use_example_data=False)
    logging.info("Graph data loaded")

    # initialize graph G (with graph class)
    G = Graph(graph=graph)

    # if the graph is empty, return
    if not G.graph:
        logging.info("Graph is empty")
        return
    shortest_time, shortest_path = G.dijkstra(start, destination, start_time)
    time_budget_shortest_path = (shortest_time - start_time) * 1  # for the shortest path, we have 100% (and not more) of the time budget
    shortest_path_reliability = compute_reliability(shortest_path, start_time, time_budget_shortest_path, transfer_time=5)
    print("Found shortest path")
    print("Shortest path:", shortest_path)
    print_path(shortest_path, start, start_time, convert_ids_to_names=True)

    # find most reliable path
    time_budget = time_budget_shortest_path * time_budget_multiplier
    # manually set higher for testing, @todo remove
    time_budget = time_budget_shortest_path * 2
    run_time_start = time.time()
    reliable_arrival_time, reliability, most_reliable_path = G.find_most_reliable_path(start, destination, start_time, int(time_budget))
    run_time_end = time.time()
    runtime = run_time_end - run_time_start

    return {
        "earliest_arrival_time": shortest_time,
        "shortest_path": shortest_path,
        "shortest_path_reliability": shortest_path_reliability,
        "most_reliable_path": most_reliable_path,
        "reliability": reliability,
        "runtime": runtime,
    }

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
    print(result["most_reliable_path"])
    print("** Result **")
    print("Earliest arrival time:", result["earliest_arrival_time"])
    print("Shortest path reliability:", result["shortest_path_reliability"])
    print("Most reliable path reliability:", result["reliability"])
    print("Runtime:", result["runtime"])

    #print(result)

