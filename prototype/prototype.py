import logging
import time
from pathlib import Path

import pandas as pd

from constants import LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL)

from algorithm.old.evaluate_shortest_paths import get_graph_data
from algorithm.graph import Graph
from algorithm.helper import (
    print_path,
    get_specific_station_identifier_from_name,
    get_specific_station_name_from_identifier,
)
from algorithm.reliability_v2 import compute_reliability


def setup_network_data(
    start, destination, start_time, end_time_interval, use_example=False
):
    if not use_example:
        # get stop ids from names
        start = get_specific_station_identifier_from_name(stop_name=start)
        destination = get_specific_station_identifier_from_name(stop_name=destination)

        # parse to number
        start = int(start)
        destination = int(destination)

    # set end time artificially (only support up to 6 hours)
    end_time = start_time + end_time_interval if end_time_interval else 120  # 2 hours

    run_time_start_generate_graph = time.time()
    # get data
    graph = get_graph_data(
        "2024-10-02",
        "../transport_data.db",
        start_time,
        end_time,
        start,
        use_example_data=use_example,
    )
    logging.info("Graph data loaded")

    run_time_end_generate_graph = time.time()
    runtime_generate_graph = run_time_end_generate_graph - run_time_start_generate_graph
    logging.info(f"Runtime for generating graph: {runtime_generate_graph} seconds")

    return graph, start, destination, runtime_generate_graph


def run_algorithms(graph, start, destination, start_time, time_budget_multiplier=1.5):
    # initialize graph G (with graph class)
    G = Graph(graph=graph)

    # if the graph is empty, return
    if not G.graph:
        logging.info("Graph is empty")
        return
    run_time_shortest_path_start = time.time()
    # find the shortest path
    shortest_time, shortest_path = G.dijkstra(start, destination, start_time)
    run_time_shortest_path_end = time.time()
    runtime_shortest_path = run_time_shortest_path_end - run_time_shortest_path_start

    # check if length of shortest is 0, if so -> no shortest path found
    if len(shortest_path) == 0:
        return {}

    time_budget_shortest_path = (
        shortest_time - start_time
    ) * 1  # for the shortest path, we have 100% (and not more) of the time budget
    shortest_path_reliability = compute_reliability(
        shortest_path, start_time, time_budget_shortest_path, transfer_time=5
    )
    logging.info("Found shortest path")
    print_path(shortest_path, start, start_time, convert_ids_to_names=True)

    # find most reliable path
    time_budget = time_budget_shortest_path * time_budget_multiplier
    run_time_start = time.time()
    reliable_arrival_time, reliability, most_reliable_path = G.find_most_reliable_path(
        start, destination, start_time, int(time_budget)
    )
    run_time_end = time.time()
    runtime = run_time_end - run_time_start

    return {
        "start_time": start_time,
        "start_station": start,
        "destination_station": destination,
        "earliest_arrival_time": shortest_time,
        "shortest_path_reliability": shortest_path_reliability,
        "runtime_shortest_path": runtime_shortest_path,  # in seconds
        "arrival_time_most_reliable_path": reliable_arrival_time,
        "reliability": reliability,
        "runtime": runtime,  # in seconds
        "shortest_path": shortest_path,
        "most_reliable_path": most_reliable_path,
    }


def find_shortest_and_most_reliable_path(
    start,
    destination,
    start_time,
    time_budget_multiplier=1.5,
    end_time_interval=120,
    use_example=False,
) -> dict:
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

    graph, start, destination, run_time_generate_graph = setup_network_data(
        start, destination, start_time, end_time_interval, use_example
    )

    result = run_algorithms(
        graph, start, destination, start_time, time_budget_multiplier
    )
    # add runtime for generating graph
    result["runtime_generate_graph"] = run_time_generate_graph
    return result


def run_multiple_test_cases(test_cases):
    for case in test_cases:
        logging.info(f"Running test case: {case}")
        start = case["start"]
        destination = case["destination"]
        start_time = case["start_time"]
        end_time_interval = case["end_time_interval"]
        time_budget_multiplier = (
            case["time_budget_multiplier"] if "time_budget_multiplier" in case else 1.5
        )
        result = find_shortest_and_most_reliable_path(
            start,
            destination,
            start_time,
            end_time_interval=end_time_interval,
            time_budget_multiplier=time_budget_multiplier,
            use_example=False,
        )
        logging.debug("** Result **")
        logging.debug("Earliest arrival time:", result["earliest_arrival_time"])
        logging.debug("Shortest path reliability:", result["shortest_path_reliability"])
        logging.debug("Most reliable path reliability:", result["reliability"])
        logging.debug("Runtime:", result["runtime"])
        logging.debug("Most reliable path route:")
        print_path(
            result["most_reliable_path"],
            start_node=result["start_station"],
            start_time=start_time,
            convert_ids_to_names=True,
        )

        # save results
        solution_path = Path("./results")
        # extract the shortest path and the most reliable path
        shortest_path = result["shortest_path"]
        most_reliable_path = result["most_reliable_path"]

        # get time budget
        time_budget = (
            result["earliest_arrival_time"] - start_time
        ) * time_budget_multiplier
        # save the time budget in the result dictionary
        result["time_budget"] = round(time_budget)

        # save these two paths in a csv file
        shortest_path_df = pd.DataFrame(shortest_path)
        path_df = pd.DataFrame(most_reliable_path)
        # go through both paths and add the station names
        shortest_path_df["from_name"] = shortest_path_df["from"].apply(
            lambda x: get_specific_station_name_from_identifier(stop_id=x)
        )
        shortest_path_df["to_name"] = shortest_path_df["to"].apply(
            lambda x: get_specific_station_name_from_identifier(stop_id=x)
        )
        path_df["from_name"] = path_df["from"].apply(
            lambda x: get_specific_station_name_from_identifier(stop_id=x)
        )
        path_df["to_name"] = path_df["to"].apply(
            lambda x: get_specific_station_name_from_identifier(stop_id=x)
        )
        shortest_path_df.to_csv(
            solution_path / f"shortest_path_{start}_{destination}_{start_time}.csv"
        )
        path_df.to_csv(
            solution_path / f"most_reliable_path_{start}_{destination}_{start_time}.csv"
        )
        # remove the paths from the result dictionary
        result.pop("shortest_path")
        result.pop("most_reliable_path")
        # also add the start and destination station names
        result["start_name"] = get_specific_station_name_from_identifier(
            stop_id=result["start_station"]
        )
        result["destination_name"] = get_specific_station_name_from_identifier(
            stop_id=result["destination_station"]
        )
        # now save results in a csv file
        # add an index to the result dictionary
        result = {k: [v] for k, v in result.items()}
        result_df = pd.DataFrame(result)
        result_df.to_csv(solution_path / f"{start}_{destination}_{start_time}.csv")


if __name__ == "__main__":
    run_multiple = True

    if run_multiple:
        # prepare multiple test cases to run
        test_cases = [
            # {
            #     "start": "Luzern",
            #     "destination": "Bern",
            #     "start_time": 600,
            #     "end_time_interval": 180
            # },
            {
                "start": "Luzern",
                "destination": "Zug",
                "start_time": 600,
                "end_time_interval": 80,
                "time_budget_multiplier": 1.5,
            },
        ]

        run_multiple_test_cases(test_cases)

    else:
        print("run single")

        start_time = 600  # 10 AM, please set this to what you need

        # you need to enter stations with their identifier, names are not supported
        # here are some examples, under "OPUIC" you can find the station identifier: https://data.sbb.ch/explore/dataset/stadtefahrplan/table/ (please without commas)
        # or just query the database (BPUIC)
        # please enter as string, otherwise it will not work
        start = "Luzern"  #
        destination = "Zug"  #

        # desired_stop_id = 8507000
        # desired_stop_name = "Bern"
        # stop = get_specific_station_identifier_from_name(stop_name="Zürich HB")
        # print(stop)
        # stop_name = get_specific_station_name_from_identifier(stop_id="8501000")
        # print("stop_name", stop_name)

        result = find_shortest_and_most_reliable_path(
            start, destination, start_time, end_time_interval=80, use_example=False
        )
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
        print_path(
            result["most_reliable_path"],
            start_node=result["start_station"],
            start_time=start_time,
            convert_ids_to_names=True,
        )
