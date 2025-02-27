# Reliable Travel Planning Prototype
---
The used Python version is 3.11.
This is a brief description of how to set up and use the project code, the folder structure and what to expect in each folder / file.
Note: GTFS data is only used for visualization. The delay data contains all necessary information for finding the paths.
---

## Setup / Running the prototype
1. Setup necessary data
    - Download the delay (and optionally GTFS) data (actual (delay) data for the desired time period: https://data.opentransportdata.swiss/en/dataset/istdaten, GTFS: https://data.opentransportdata.swiss/en/?groups=timetables-gtfs)
    - Set up the delay database (and optionally GTFS database) with the data (see the setup delay data folder and setup GTFS data optional folder)
2. Choose desired start and destination station as well as the start time and run the prototype.py file (in the prototype folder) to generate the results - the results are stored in the "results" folder.
    - It is also possible to run multiple scenarios at once (by providing a list of start and destination stations and start times).
    - Additional parameters are the end time interval and the time budget multiplier.
3. Visualizing the results (optional)
    - Run the "create_graph_visual_from_results.py file" in the visualization folder to visualize the results (the paths and reliability information).
    - The visualization is based on the results in the prototype/results folder.
---

### Note
There is a reference to a data folder with the GTFS and delay data (and also a database 'transport.db' in the root folder) - because of the size of these files, they are not included in git. They need to be created separately.
Also, some databases created for querying data live in the data folder.
PyCharm is used as the IDE for this project.
### Packages
We currently use duck db as database for querying the data (GTFS and actual (delay) data). We use networkx for visualizing the graphs (could have used it for finding the shortest path as well, but we decided to code that ourselves (for understanding and better ability to customize the code). For some data manipulations we use pandas and numpy.
Also, we use 'logging' for testing, debugging and progress updates.

---
# Folder structure

## constants.py
Currently only used for setting the log level (meaning either logging only a few messages - INFO - or a lot of messages for debugging/testing - DEBUG). Note: logging can significantly slow down the program.

## algorithm folder
This folder contains the most important files for this project: the implementation of the algorithms. graph.py contains the dijkstra shortest path algorithm and the network search for finding the most reliable path/itinerary.
The reliability.py file contains the implementation of the reliability calculation (based on the delay data).

## prototype folder
Here is the implementation for testing and evaluating the algorithms.
prototype.py is used for running different scenarios (origin, destination combinations, etc.)).
app.py contains the implementation of the Flask app for the prototype (it is a simple web app for how the prototype could be used or look like).
### results
This folder contains the results of running the prototype.py file (the different scenarios).
The results are stored in csv files (for easy reading and further analysis). For each scenario, there is one general csv file containing the overall results (earliest possible arrival, reliability, runtime, ...).
And two files with the shortest path and the most reliable path for each scenario.
The file names start with the starting station, destination station and the start time. The name also contains information whether efficiency improvements were applied or not.
### templates
This folder contains the html files for the Flask app (app.py).

## retrieve data folder
The file in this folder builds the network graph for the algorithms by querying the delay data (actual data) and then transforming it into a suitable format for the algorithms.

## setup delay data folder
Here are functions for setting up the delay database (which is primarily used in this project).
The GTFS data contains more information about stops and routes, etc. (such as the lat/lon coordinates of the stops, which are used for visualization purposes).

## setup GTFS data optional folder
This folder contains functions for setting up the GTFS database (which is optional, since the delay data contains all necessary information for finding the paths).
Necessary for visualization purposes (lat/lon coordinates of the stops).
The "create_gtfs_db_full" and "create_script_gtfs_tables_db" files contain database statements for importing the GTFS data into duck db (which is quite comfortable for querying the GTFS data, the structure is the same as in the files - with a separate table for routes, trips, stops, etc.).

## visualization folder
This folder contains the implementation for visualizing the network graph based on the results in the prototype/results folder.

## data tinker folder
Here are some data exploration files (like data-exploration.py). These were used for data exploration and analysis purposes and also the initial versions of querying delay and GTFS data for the network generation.

## old folder
This folder contains some old files that were used for testing and experimenting with the data and the algorithms. They are not used in the current version of the prototype.
However, some files contain still partially relevant code (like the example we used initially for the reliability calculation to compare with the pen & paper results).