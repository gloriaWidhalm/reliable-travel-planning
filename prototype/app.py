from flask import Flask, render_template, request
from algorithm.graph import Graph
from algorithm.reliability import compute_reliability


app = Flask(__name__)

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

G = Graph(graph=graph)


# ---------------------------------------------------------------------------
# A sample list of stations. In real usage, you might retrieve these
# from a database or API.
# ---------------------------------------------------------------------------
STATIONS = list(graph.keys())


def get_paths(departure_station: str, arrival_station: str, departure_time: int):
    # Example mock data for demonstration:
    # shortest_time, shortest_path = G.dijkstra(departure_station, arrival_station, departure_time)
    shortest_time, shortest_path_result = G.dijkstra(
        departure_station, arrival_station, departure_time, transfer_time=5
    )

    # @todo - for simplicity, very high time budget is used
    time_budget = (
        shortest_time - departure_time
    ) * 3  # for the shortest path, we have 100% (and not more) of the time budget

    shortest_path = _map_path_to_tuples(shortest_path_result)
    shortest_path_reliability = compute_reliability(
        shortest_path_result,
        departure_time,
        (shortest_time - departure_time) * 1,
        transfer_time=5,
    )

    arrival_time, reliability, most_reliable_path_result = G.find_most_reliable_path(
        departure_station, arrival_station, departure_time, int(time_budget)
    )
    print("Arrival time: ", arrival_time)
    print("most reliable path result ", most_reliable_path_result)

    most_reliable_path = _map_path_to_tuples(most_reliable_path_result)
    most_reliable_path_reliability = reliability

    # Calculate the arrival time difference between the shortest path and the most reliable path
    difference = (
        most_reliable_path_result[-1]["planned_arrival"]
        - shortest_path_result[-1]["planned_arrival"]
    )
    print("Shortest path: ", shortest_path)
    print("Most reliable path: ", most_reliable_path)

    return (
        shortest_path,
        shortest_path_reliability,
        most_reliable_path,
        most_reliable_path_reliability,
        difference,
    )


def _map_path_to_tuples(path: list) -> list:
    return [
        (
            f"{x['trip_id']} {x['from']}",
            x["to"],
            _convert_minutes_to_time(x["planned_departure"]),
            _convert_minutes_to_time(x["planned_arrival"]),
        )
        for x in path
    ]


def _convert_time_to_minutes(time: str) -> int:
    hours, minutes = map(int, time.split(":"))
    return hours * 60 + minutes


def _convert_minutes_to_time(minutes: int) -> str:
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours:02d}:{minutes:02d}"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        departure_station = request.form.get("departure_station").strip()
        arrival_station = request.form.get("arrival_station").strip()
        departure_time = request.form.get("departure_time").strip()

        # Convert to minutes
        departure_time_minutes = _convert_time_to_minutes(departure_time)
        # @TODO: change this
        # departure_time_minutes = 400

        # Call the internal python function
        (
            shortest_path,
            shortest_path_reliability,
            most_reliable_path,
            most_reliable_path_reliability,
            difference,
        ) = get_paths(departure_station, arrival_station, departure_time_minutes)

        print("most_reliable_path: ", most_reliable_path)
        print("shortest_path: ", shortest_path)

        return render_template(
            "results.html",
            departure_station=departure_station,
            arrival_station=arrival_station,
            departure_time=departure_time,
            shortest_path=shortest_path,
            shortest_path_reliability=shortest_path_reliability,
            most_reliable_path=most_reliable_path,
            most_reliable_path_reliability=most_reliable_path_reliability,
            difference=difference,
        )

    # If GET request, just render the form and include the station list
    return render_template("index.html", stations=STATIONS)


if __name__ == "__main__":
    app.run(debug=True)
