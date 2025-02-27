import logging
import time
from pathlib import Path

import pandas as pd

from constants import LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL)


from algorithm.graph import Graph
from algorithm.helper import (
    print_path,
    get_specific_station_identifier_from_name,
    get_specific_station_name_from_identifier, get_graph_data,
)
from algorithm.reliability import compute_reliability


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


def run_algorithms(graph, start, destination, start_time, time_budget_multiplier=1.5, enable_efficiency_improvements=True):
    # initialize graph G (with graph class)
    G = Graph(graph=graph)

    # if the graph is empty, return
    if not G.graph:
        logging.info("Graph is empty")
        return
    run_time_shortest_path_start = time.time()
    # find the shortest path
    shortest_time, shortest_path = G.dijkstra(start, destination, start_time)
    # check if the shortest path is empty
    if not shortest_path or len(shortest_path) == 0:
        return {}
    run_time_shortest_path_end = time.time()
    runtime_shortest_path = run_time_shortest_path_end - run_time_shortest_path_start

    # check if length of shortest is 0, if so -> no shortest path found
    if len(shortest_path) == 0:
        return {}

    # for the shortest path, we have 100% (and not more) of the time budget
    time_budget_shortest_path = (
        shortest_time - start_time
    ) * 1 # + 5 # add 5 minutes for reliability assessment, assuming 5 minutes later is still acceptable
    shortest_path_reliability = compute_reliability(
        shortest_path, start_time, time_budget_shortest_path, transfer_time=5
    )
    logging.info("Found shortest path")
    print_path(shortest_path, start, start_time, convert_ids_to_names=True)

    # find most reliable path
    time_budget = time_budget_shortest_path * time_budget_multiplier
    run_time_start = time.time()
    # set the initial most reliable path to the shortest path
    initial_most_reliable_path = (
        shortest_path_reliability,
        1,
        shortest_time - start_time,
        shortest_path_reliability, # this would be probability arrival for partial itineraries
        shortest_path,
    )
    reliable_arrival_time, reliability, most_reliable_path = G.find_most_reliable_path(
        start, destination, start_time, int(time_budget), lower_bound_reliability=shortest_path_reliability, initial_most_reliable_path=initial_most_reliable_path, enable_efficiency_improvements=enable_efficiency_improvements
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
    enable_efficiency_improvements=True,
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
        graph, start, destination, start_time, time_budget_multiplier, enable_efficiency_improvements=enable_efficiency_improvements
    )
    # check if the result is empty
    if not result or len(result.values()) == 0:
        return {}
    # add runtime for generating graph
    result["runtime_generate_graph"] = run_time_generate_graph
    return result

def run_single_case(start, destination, start_time, end_time_interval, time_budget_multiplier=1.5, enable_efficiency_improvements=True):
    logging.info(f"Running test case: {start} to {destination} at {start_time} with time interval {end_time_interval} and time budget multiplier {time_budget_multiplier}, efficiency improvements: {enable_efficiency_improvements}")
    result = find_shortest_and_most_reliable_path(
        start,
        destination,
        start_time,
        end_time_interval=end_time_interval,
        time_budget_multiplier=time_budget_multiplier,
        enable_efficiency_improvements=enable_efficiency_improvements,
        use_example=False,
    )
    if len(result.values()) == 0:
        logging.info("No solution could be found.")
        return {}

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
    return result

def run_multiple_test_cases(test_cases, enable_efficiency_improvements=True, create_average_run_time=False):
    for case in test_cases:
        start = case["start"]
        destination = case["destination"]
        # start time -> arrival (and departure) must be after this time
        start_time = case["start_time"]
        # end time interval -> departure must be before this time
        end_time_interval = case["end_time_interval"]
        time_budget_multiplier = (
            case["time_budget_multiplier"] if "time_budget_multiplier" in case else 1.5
        )
        if create_average_run_time:
            # create an average run time for finding the most reliable path (other run times are not averaged)
            logging.info("Creating average run time")
            run_times = []
            run_times_graph_generation = []
            run_times_shortest_path = []
            result = {}
            # running the test case 2 times to get an average run time
            for i in range(2):
                result = run_single_case(start, destination, start_time, end_time_interval, time_budget_multiplier, enable_efficiency_improvements=enable_efficiency_improvements)
                # if result is empty, continue with the next test case
                if len(result.values()) == 0:
                    continue
                run_times.append(result["runtime"])
                run_times_graph_generation.append(result["runtime_generate_graph"])
                run_times_shortest_path.append(result["runtime_shortest_path"])
            if len(run_times) == 0:
                logging.debug(f"No solution could be found for test case {start} to {destination} at {start_time} with time interval {end_time_interval} and time budget multiplier {time_budget_multiplier}")
                continue
            average_runtime = sum(run_times) / len(run_times)
            average_runtime_generate_graph = sum(run_times_graph_generation) / len(run_times_graph_generation)
            average_runtime_shortest_path = sum(run_times_shortest_path) / len(run_times_shortest_path)
            # overwrite the runtime with the average runtime, we assume all other values are the same
            result["runtime"] = average_runtime # this is the runtime for finding the most reliable path
            result["runtime_generate_graph"] = average_runtime_generate_graph
            result["runtime_shortest_path"] = average_runtime_shortest_path
        else:
            result = run_single_case(start, destination, start_time, end_time_interval, time_budget_multiplier, enable_efficiency_improvements=enable_efficiency_improvements)

        if len(result.values()) == 0:
            logging.info(f"No solution could be found for test case {start} to {destination} at {start_time} with time interval {end_time_interval} and time budget multiplier {time_budget_multiplier}")
            continue
        # save results
        solution_path = Path("../prototype/results")
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
        file_name_prefix = f"{start}_{destination}_{start_time}"
        if enable_efficiency_improvements:
            file_name_prefix += "_with_eff_impr"
        # check if the file already exists, if so, add a number to the file name and check again
        file_number = 1
        while (solution_path / f"{file_name_prefix}_{file_number}.csv").exists():
            file_number += 1
        file_name_prefix = f"{file_name_prefix}_{file_number}"
        logging.info(f"Saving results to {solution_path / f'{file_name_prefix}.csv'}")
        shortest_path_df.to_csv(
            solution_path / f"{file_name_prefix}_shortest_path.csv"
        )
        path_df.to_csv(
            solution_path / f"{file_name_prefix}_most_reliable_path.csv"
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
        result_df.to_csv(solution_path / f"{file_name_prefix}.csv")


if __name__ == "__main__":
    create_average_run_time = False
    enable_efficiency_improvements = True

    # prepare multiple test cases to run
    test_cases = [
        # {
        #     "start": "Luzern",
        #     "destination": "Bern",
        #     "start_time": 600,
        #     "end_time_interval": 180,
        #     "time_budget_multiplier": 1.5,
        # },
        # {
        #     "start": "Luzern",
        #     "destination": "Rotkreuz",
        #     "start_time": 600,
        #     "end_time_interval": 60,
        #     "time_budget_multiplier": 1.5,
        # },
        {
            "start": "Luzern",
            "destination": "Zug",
            "start_time": 600,
            "end_time_interval": 80,
            "time_budget_multiplier": 1.5,
        },
        # {
        #     "start": "Luzern",
        #     "destination": "Olten",
        #     "start_time": 600,
        #     "end_time_interval": 120,
        #     "time_budget_multiplier": 1.5,
        # },
        # {
        #     "start": "Luzern",
        #     "destination": "Pfäffikon",
        #     "start_time": 600,
        #     "end_time_interval": 120,
        #     "time_budget_multiplier": 1.5,
        # },
        # {
        #     "start": "Brig",
        #     "destination": "Freiburg",
        #     "start_time": 600,
        #     "end_time_interval": 240,
        #     "time_budget_multiplier": 1.5,
        # },
    ]

    run_multiple_test_cases(test_cases, enable_efficiency_improvements=enable_efficiency_improvements, create_average_run_time=create_average_run_time)