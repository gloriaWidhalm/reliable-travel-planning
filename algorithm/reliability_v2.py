from copy import deepcopy
from typing import List
import logging

from algorithm.helper import is_transfer_needed
from constants import LOG_LEVEL

TRANSFER_TIME_DEFAULT = 5
# set log level
logging.basicConfig(level=LOG_LEVEL)


def compute_probability(time: int, time_distribution: List[int]) -> float:
    """
    Compute the probability of a train departing or arriving at a given time given a list of departure times or arrival times
    """
    # count the number of trains departing/arriving at the given time
    count = time_distribution.count(time)
    # count the total number of trains
    total = len(time_distribution)
    # compute the probability
    probability = count / total
    return probability


# Add the departure time probabilities to the data (for each trip), they don't change
def add_departure_probabilities(station_trips: List[dict]):
    """
    Add the departure time probabilities to the data
    We assume the trains do not wait for other delayed trains
    """
    for trip in station_trips:
        # get the actual departure times
        actual_departure_times = [
            actual_time[0] for actual_time in trip["actual_times"]
        ]
        # for each actual departure time, compute the probability of departing at that time
        departure_probabilities = [
            (time, compute_probability(time, actual_departure_times))
            for time in actual_departure_times
        ]
        # only use unique departure probabilities
        departure_probabilities = list(set(departure_probabilities))
        # add the departure probabilities to the trip
        trip["departure_probabilities"] = departure_probabilities


def get_all_arrival_probabilities_trip(
        arrival_times: List[int],
) -> List[tuple[int, float]]:
    """
    Get all arrival probabilities for a given trip
    """
    # get the actual arrival times
    # for each actual arrival time, compute the probability of arriving at that time
    arrival_probabilities = [
        (time, compute_probability(time, arrival_times)) for time in arrival_times
    ]
    # only use unique arrival probabilities
    arrival_probabilities = list(set(arrival_probabilities))
    logging.debug(f"Arrival probabilities first trip: {arrival_probabilities}, Arrival times first trip: {arrival_times}")
    return arrival_probabilities


def get_arrival_times_from_trip(trip: dict) -> List[int]:
    """
    Get the arrival times distribution for a given trip
    """
    # get the actual arrival times
    actual_arrival_times = [actual_time[1] for actual_time in trip["actual_times"]]
    return actual_arrival_times


def compute_probability_to_arrive_at_or_before(
        time_limit: int,
        arrival_probabilities: List[tuple[int, float]],
        arrival_times: List[int],
) -> float:
    """
    Compute the probability of arriving at or before a given time given a list of arrival probabilities that were calculated beforehand
    """
    # get first (minimum) arrival time
    min_arrival_time = min(
        arrival_times
    )  # @todo: note: should be the first if we get a sorted list -> would be more efficient
    # get last (maximum) arrival time -> either the latest arrival time or the time limit if that is earlier
    max_arrival_time = min(
        max(arrival_times), time_limit
    )  # @todo: note: should be the last if we get a sorted list -> would be more efficient

    # if we have arrival probabilities given, we can use them directly (e.g., probability to arrive at time t' given that we made the connection)
    probabilities = [
        arrival_time[1]
        for arrival_time in arrival_probabilities
        if arrival_time[0] <= max_arrival_time
    ]
    logging.debug(f"Arrival probabilities: {probabilities}, arrival times: {arrival_times}, compute_probability_to_arrive_at_or_before")
    # sum the probabilities
    probability = sum(probabilities)
    return probability


def compute_connection_probability(
        departure_probabilities: List[tuple[int, float]],
        arrival_probabilities: List[tuple[int, float]],
        arrival_times: List[int],
        transfer_needed: bool,
        transfer_time=TRANSFER_TIME_DEFAULT,
) -> float:
    """
    Compute the probability of making a connection given a list of departure times and a list of arrival time probabilities
    """
    # for each departure time, compute the probability of making a connection
    probabilities = []
    # multiply probability of departing at time t with the probability of arriving at or before time (t - transfer time)
    for i in range(len(departure_probabilities)):
        # only consider the arrival time probabilities that are before the departure time - transfer time
        # check if we need a transfer (or if we are in the same train)
        time_limit = (
            departure_probabilities[i][0] - transfer_time
            if transfer_needed
            else departure_probabilities[i][0]
        )
        arrival_probability = compute_probability_to_arrive_at_or_before(
            time_limit, arrival_probabilities, arrival_times
        )
        probabilities.append(departure_probabilities[i][1] * arrival_probability)
        logging.debug(f"Departure time: {departure_probabilities[i][0]}, departure probabilities {departure_probabilities[i][1]} Arrival probability: {arrival_probability}, arrival times: {arrival_times}")
        logging.debug(f"**Probabilities for connection made: {probabilities}, sum: {sum(probabilities)}")
    # sum the probabilities
    probability = sum(probabilities)
    # return the probability of a connection made
    return probability


def compute_probability_to_arrive_at_t_given_connection_made(
        arrival_time: int,
        departure_probabilities: List,
        arrival_probabilities: List | None,
        arrival_times: List[int],
        probability_connection_made: float,
        arrival_departure_tuples: List,
        transfer_needed: bool,
        transfer_time=5,
) -> float:
    """Compute the probability of arriving at time t given that we made the connection."""
    probabilities = []
    # loop through all possible departure times
    for t_dep in departure_probabilities:
        # conditional probability of arriving at time t given the departure at t'
        # To compute this conditional probability, we need to count how often an arrival-departure pair occurs (divided by total number of arrival-departure pairs)
        # and then divide by the probability that we depart at t'
        occurence_arrival_departure_pair = (
            0  # how often the arrival-departure pair occurs
        )
        for pair in arrival_departure_tuples:
            if t_dep[0] == pair[0] and arrival_time == pair[1]:
                occurence_arrival_departure_pair += 1
        # probability of arriving at time t given that we depart at t'
        probability_arrival_at_t_given_departure_at_t_prime = (
                occurence_arrival_departure_pair / len(arrival_departure_tuples)
        )

        # probability of departing at time t'
        probability_departure = t_dep[1]
        # probability of arriving at time t given that we depart at t'
        probability_arrival_given_departure = (
                probability_arrival_at_t_given_departure_at_t_prime / probability_departure
        )

        # probability of arriving at or before t' given the arrival probabilities
        # check if the transfer is needed, if yes, we need to consider the transfer time
        time_limit = t_dep[0] - transfer_time if transfer_needed else t_dep[0]
        probability_arrival_before_t_prime = compute_probability_to_arrive_at_or_before(
            time_limit, arrival_probabilities, arrival_times
        )

        logging.debug(f"Departure time: {t_dep[0]}, Arrival time: {arrival_time}")
        logging.debug(f"Departure probability: {probability_departure}")
        logging.debug(f"Arrival probability before t': {probability_arrival_before_t_prime}")
        logging.debug(f"Arrival probability given departure: {probability_arrival_given_departure}")
        logging.debug(f"Probability connection made: {probability_connection_made}")

        # check if the probability of connection made is 0, if yes, we return 0
        if probability_connection_made == 0:
            return 0 # otherwise we would divide by 0, #@todo -> maybe break better here?
        # conditional probability of arriving at time t given that we made the connection
        probability = (
                              probability_departure
                              * probability_arrival_before_t_prime
                              * probability_arrival_given_departure
                      ) / probability_connection_made

        logging.debug(f"Probability of arriving at time {arrival_time} given that we made the connection: {probability}")

        # sum later over all departure times
        probabilities.append(probability)
    probability_sum = sum(probabilities)

    return probability_sum


def compute_arrival_probability_last_trip(start_time: int, time_budget: int, arrival_probabilities: List[tuple[int, float]], arrival_times: List[int]):
    """
    Compute the probability of arriving at the destination at or before the time limit for the last trip
    """
    time_limit = start_time + time_budget
    #logging.debug(f"Arrival probabilities last trip: {arrival_probabilities}, Arrival times last trip: {arrival_times}")
    probability_arrival_before_time_limit = compute_probability_to_arrive_at_or_before(
        time_limit, arrival_probabilities, arrival_times
    )
    return probability_arrival_before_time_limit


def compute_reliability(
        station_trips: List[dict],
        start_time: int,
        time_budget: int,
        complete_path = True, # whether we want the reliability for a partial path (sequence of trips) or a complete one
        transfer_time=TRANSFER_TIME_DEFAULT,
) -> float | tuple[float, float]:
    """
    Compute the reliability of a connection given a list of trips and a start time and time budget
    station_trips because it is a dictionary with the station as key and the trips from this station as values
    """
    logging.debug(f"#########################################")
    logging.debug(f"Compute reliability for station trips: {station_trips}")
    # First, add the departure probabilities to the trips
    # create a deep copy of the station trips to avoid modifying the original data
    station_trips_copy = deepcopy(station_trips)

    # different handling / exception: if the first trip is our start (meaning "from" and "to" are the same node/station, we skip this trip and take the next one)
    if station_trips_copy[0]["from"] == station_trips_copy[0]["to"]:
        # remove the first trip from the station trips
        station_trips_copy = station_trips_copy[1:]

    add_departure_probabilities(station_trips_copy)

    # different handling depending on the number of trips
    # if the length is 0, we return 0
    if len(station_trips_copy) == 0:
        return 0, 0

    # extract the first trip from the station trips
    first_trip = station_trips_copy[0]  # for a path, we have always only one trip per station, therefore we can use [0]
    #logging.debug(f"First trip: {first_trip}")

    # get arrival times and arrival probabilities for the first trip
    arrival_times_first_trip = get_arrival_times_from_trip(first_trip)
    arrival_probabilities_first_trip = get_all_arrival_probabilities_trip(
        arrival_times_first_trip
    )

    # if the length is 1, we return the probability of arriving at the destination at or before the time limit
    if len(station_trips_copy) == 1:
        if not complete_path:
            return compute_arrival_probability_last_trip(
                start_time, time_budget, arrival_probabilities_first_trip, arrival_times_first_trip
            ), 1 # the connection is always made, because we only have one trip
        return compute_arrival_probability_last_trip(
            start_time, time_budget, arrival_probabilities_first_trip, arrival_times_first_trip
        )
    logging.debug("-----------------------------")
    # extract the second trip from the station trips (also handled a bit differently)
    second_trip = station_trips_copy[1]
    #logging.debug(f"Second trip: {second_trip}")
    # all the trips from the third trip onwards until the last trip
    trips_from_third_trip = station_trips_copy[2:]
    # compute the probability of making the first connection (between the first and second trip)
    # check if a transfer is needed between the first and second trip
    transfer_needed_first_second_trip = is_transfer_needed(
        first_trip["trip_id"] if "trip_id" in first_trip else "", second_trip["trip_id"] if "trip_id" in second_trip else ""
    )
    connection_made_first_second_trip = compute_connection_probability(
        second_trip["departure_probabilities"],
        arrival_probabilities_first_trip,
        arrival_times_first_trip,
        transfer_needed_first_second_trip,
        transfer_time,
    )
    # compute arrival probabilities for second trip given that we made the connection (between the first and second trip)
    arrival_times_second_trip = get_arrival_times_from_trip(second_trip)
    arrival_probabilities_second_trip = []
    # loop through the arrival times of the second trip and compute the probability of arriving at that time given that we made the connection
    for arrival_time in arrival_times_second_trip:
        probability = compute_probability_to_arrive_at_t_given_connection_made(
            arrival_time,
            second_trip["departure_probabilities"],
            arrival_probabilities_first_trip,
            arrival_times_first_trip,
            connection_made_first_second_trip,
            second_trip["actual_times"],
            transfer_needed_first_second_trip,
            transfer_time,
        )
        arrival_probabilities_second_trip.append((arrival_time, probability))
    # only use unique arrival probabilities
    arrival_probabilities_second_trip = list(set(arrival_probabilities_second_trip))

    # check if the length is 2, if yes, we return the probability of arriving at the destination at or before the time limit multiplied by the probability of
    # making the first connection as reliability
    if len(station_trips_copy) == 2:
        probability_arrival_before_time_limit = compute_arrival_probability_last_trip(
            start_time, time_budget, arrival_probabilities_second_trip, arrival_times_second_trip
        )
        # If we want to know the reliability of a partial path (not complete), then we return the probabilities separately
        if not complete_path:
            return probability_arrival_before_time_limit, connection_made_first_second_trip
        return probability_arrival_before_time_limit * connection_made_first_second_trip

    logging.debug("-----------------------------")

    is_third_trip = True  # different handling for the third trip

    # prepare the data for the reliability computation
    last_trip_arrival_probabilities = []  # arrival probabilities
    last_trip_connection_made = -1  # initialize with 1, if we have no connection, the probability is 1
    last_trip_arrival_times = []  # arrival times

    # compute the rest of the connections (from the third trip onwards), connection probability and arrival probabilities given that we made the connection
    # first, we handle the case of the third trip (preparing the data we need for the probability computation)
    # then, we compute the connection probability, and the arrival probabilities given that we made the connection
    # then, we prepare the data for the next trip (iteration)
    # we repeat this for all trips after the second trip
    for current_trip in trips_from_third_trip:
        #logging.debug(f"Current trip: {current_trip}")
        if is_third_trip:
            previous_trip = second_trip
            arrival_probabilities_previous_trip = arrival_probabilities_second_trip
            arrival_times_previous_trip = arrival_times_second_trip
            connection_made_previous_trip = connection_made_first_second_trip
            is_third_trip = False

        transfer_needed = is_transfer_needed(previous_trip["trip_id"] if "trip_id" in previous_trip else "", current_trip["trip_id"] if "trip_id" in current_trip else "")
        arrival_times = get_arrival_times_from_trip(current_trip)
        arrival_probabilities = []

        # compute the probability of making the connection (between the previous and current trip)
        connection_made = compute_connection_probability(
            current_trip["departure_probabilities"],
            arrival_probabilities_previous_trip,
            arrival_times_previous_trip,
            transfer_needed,
            transfer_time,
        )

        # compute arrival probabilities for the current trip given that we made the connection (between the previous and current trip)
        for arrival_time in arrival_times:
            probability = compute_probability_to_arrive_at_t_given_connection_made(
                arrival_time,
                current_trip["departure_probabilities"],
                arrival_probabilities_previous_trip,
                arrival_times_previous_trip,
                connection_made,
                current_trip["actual_times"],
                transfer_needed,
                transfer_time,
            )
            arrival_probabilities.append((arrival_time, probability))
        # only use unique arrival probabilities
        arrival_probabilities = list(set(arrival_probabilities))
        logging.debug(f"### Arrival probabilities in loop {arrival_probabilities}")

        # at the end of this iteration, we prepare the previous trip for the next iteration
        previous_trip = current_trip
        arrival_probabilities_previous_trip = arrival_probabilities
        arrival_times_previous_trip = arrival_times
        connection_made_previous_trip = connection_made

        # store the arrival probabilities of the last trip and the connection probability for the final reliability computation
        last_trip_arrival_probabilities = arrival_probabilities
        last_trip_connection_made = connection_made
        last_trip_arrival_times = arrival_times

        logging.debug("-----------------------------")



    # compute the reliability of the connection
    # first, compute the part where we check if we arrive at the destination at or before the time limit
    # then, we multiply this with the probability of making the last connection

    probability_arrival_before_time_limit = compute_arrival_probability_last_trip(
        start_time, time_budget, last_trip_arrival_probabilities, last_trip_arrival_times
    )
    #logging.debug(f"Probability of arriving at the destination at or before the time limit: {probability_arrival_before_time_limit}")
    # if the last trip connection made is -1, throw exception
    if last_trip_connection_made == -1:
        raise ValueError("No connection made for the last trip")

    # If we want to know the reliability of a partial path (not complete), then we return the probabilities separately
    if not complete_path:
        return probability_arrival_before_time_limit, last_trip_connection_made

    reliability = probability_arrival_before_time_limit * last_trip_connection_made
    return reliability


if __name__ == "__main__":
    # for testing reliability.py
    # this is intermediate data to test the algorithm
    # use a dictionary structure for each trip, so we can extend it with additional information
    # this is the output from the dijkstra algorithm (for our simple IC8 example)
    # @todo -> output from dijkstra algorithm (shortest path) as list of dictionaries (the order is important!)
    # @todo -> still would need to change the output of the shortest path (not list of dictionaries with stations (and then nested the trips) but just list of dictionaries as trips)
    station_trips = [
        {
            "from": "Bern",
            "to": "Thun",
            "planned_departure": 487,
            "planned_arrival": 505,
            "trip_id": "IC8",
            "actual_times": [(487, 505), (490, 508)],
        },
        {
            "from": "Thun",
            "to": "Spiez",
            "planned_departure": 506,
            "planned_arrival": 516,
            "trip_id": "IC8",
            "actual_times": [(506, 516), (509, 519)],
        },
        {
            "from": "Spiez",
            "to": "Visp",
            "planned_departure": 516,
            "planned_arrival": 542,
            "trip_id": "IC8",
            "actual_times": [(516, 542), (519, 545)],
        },
        {
            "from": "Visp",
            "to": "Brig",
            "planned_departure": 543,
            "planned_arrival": 551,
            "trip_id": "IC8",
            "actual_times": [(543, 551), (546, 554)],
        }
    ]
    earliest_possible_arrival = 551  # based on dijkstra

    # initialize the start time and time budget
    start_time = 400
    # time budget is 1.5 of the earliest possible arrival time
    time_budget = (earliest_possible_arrival - start_time) * 1
    # round to the next full minute
    time_budget = round(time_budget)

    # compute the reliability of the connection
    reliability = compute_reliability(
        station_trips, start_time, time_budget, transfer_time=1
    )
    logging.info("Start time:", start_time, "Time budget:", time_budget, "Earliest possible arrival:", earliest_possible_arrival, "Latest possible arrival:", start_time + time_budget)
    logging.info("Reliability of the connection:", reliability)

    # @todo: integrate the probability of cancellations (e.g. extreme late arrivals?)
