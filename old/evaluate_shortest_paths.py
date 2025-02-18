# This file contains code to run the simple Dijsktra pathfinder
from algorithm.helper import get_graph_data
from old.main import print_path
from constants import LOG_LEVEL
from algorithm.graph import Graph
from algorithm.reliability_v2 import compute_reliability

import logging


logging.basicConfig(level=LOG_LEVEL)


if __name__ == "__main__":
    # Code to evaluate different shortest paths

    start_time = 540  # 0 minutes, please set this to what you need
    end_time = 720  # 24 hours, please set this to what you need

    # you need to enter stations with their identifier, names are not supported
    # here are some examples, under "OPUIC" you can find the station identifier: https://data.sbb.ch/explore/dataset/stadtefahrplan/table/ (please without commas)
    # or just query the database
    logging.info("Loading graph data")
    # please enter as number, otherwise it will not work
    start = 8501003  # Sissach
    destination = 8501000  # Zimeysa

    # get data
    graph = get_graph_data(
        "2024-10-02",
        "../transport_data.db",
        start_time,
        end_time,
        start,
        use_example_data=False,
    )
    logging.info("Graph data loaded")

    # idea: could define a list of start node, start time and destination node and loop over it, then save the results in a pandas dataframe and export it to a csv file (for further analysis)

    # initialize graph G (with graph class)
    G = Graph(graph=graph)

    # logging.debug("Graph: ")
    # logging.debug(G.graph)

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
