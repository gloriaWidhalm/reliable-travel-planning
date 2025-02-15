import pandas as pd
from matplotlib import pyplot as plt

from algorithm.graph import Graph
from algorithm.helper import get_coordinates_from_station_list, get_specific_trip_identifier_from_identifier, minutes_to_time
from visualization.plot_graph import plot_graph


def get_graph_and_stations_from_path(path):
    # get all stations as a list with their names and coordinates
    stations_path = []
    for i, row in path.iterrows():
        from_station = row["from_name"]
        to_station = row["to_name"]
        stations_path.append(from_station)
        stations_path.append(to_station)
    # make sure to remove duplicates
    stations_path = list(set(stations_path))

    path_coordinates = get_coordinates_from_station_list(station_list=stations_path)

    # create graph from the path (for the visualization)
    graph_dictionary = {}
    # add edges to the graph
    for i, row in path.iterrows():
        from_station = row["from_name"]
        to_station = row["to_name"]
        trip_id = get_specific_trip_identifier_from_identifier(trip_id=row["trip_id"])
        # departure, arrival and actual times not relevant for the visualization
        graph_dictionary[from_station] = [(0, to_station, 0, trip_id)]

    return graph_dictionary, path_coordinates

def get_station_map_from_station_coordinates(stations: pd.DataFrame):
    # get stations dictionary from dataframe
    stations = stations.to_dict(orient='records')
    # map stations for graph visualization: {"stop_name": [stop_lat, stop_lon]}
    stations_map = {stop['stop_name']: [stop['stop_lon'], stop['stop_lat']] for stop in stations}
    return stations_map

if __name__ == "__main__":
    # read in the results (shortest path and most reliable path)
    results_file = "Luzern_Zug_600"
    shortest_path = pd.read_csv(f"../prototype/results/shortest_path_{results_file}.csv")
    most_reliable_path = pd.read_csv(f"../prototype/results/most_reliable_path_{results_file}.csv")
    # get start, destination and start time
    results_metadata = pd.read_csv(f"../prototype/results/{results_file}.csv")
    start = results_metadata["start_name"].iloc[0]
    destination = results_metadata["destination_name"].iloc[0]
    start_time = results_metadata["start_time"].iloc[0]
    earliest_arrival_time = results_metadata["earliest_arrival_time"].iloc[0]
    most_reliable_arrival_time = results_metadata["arrival_time_most_reliable_path"].iloc[0]

    shortest_path_graph, shortest_path_coordinates = get_graph_and_stations_from_path(shortest_path)
    most_reliable_path_graph, most_reliable_path_coordinates = get_graph_and_stations_from_path(most_reliable_path)

    # get map for stations
    shortest_path_station_map = get_station_map_from_station_coordinates(shortest_path_coordinates)
    most_reliable_path_station_map = get_station_map_from_station_coordinates(most_reliable_path_coordinates)

    # plot the graphs
    plot_graph(shortest_path_graph, pos=shortest_path_station_map, title=f"Shortest path between {start} and {destination}, \n starting at {minutes_to_time(start_time)} and arriving at {minutes_to_time(earliest_arrival_time)}", save=True, filename=f"shortest_path_{results_file}.png")
    plot_graph(most_reliable_path_graph, pos=most_reliable_path_station_map, title=f"Most reliable path between {start} and {destination}, \n starting at {minutes_to_time(start_time)} and arriving at {minutes_to_time(most_reliable_arrival_time)}", save=True, filename=f"most_reliable_path_{results_file}.png", edge_color="purple")
