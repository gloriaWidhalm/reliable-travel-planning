# Reliable Travel Planning Prototype

This is a brief descriptions of the folder structure and what to expect at each folder / file.

---

### Note
There is a reference to a data folder with the GTFS and delay data - because of the size of these files, they are not included in git. They need to be downloaded individually.
Also, the databases creating for querying live in the data folder.
### Packages
We currently use duck db as database for querying the data (GTFS and actual data). We currently use networkx in one implementation (simple prototype) but it might be part of the final solution. For some data manipulations we use pandas.

---
# Folder structure
## Data tinker folder
Here are some data exploration files (like data-exploration.py). The Jupyter notebooks data_tinker_actual_data and data_tinker_gtfs_db are there for finding out how to join / merge the GFTS data with the delay data.

## Prototype-Dijkstra folder
Here is the implementation for finding the shortest path via the Dijkstra algorithm. It is a bit closer to a real-world scenario than the simple prototype (that was only for experimentation).

## Simple prototype experimentation folder
In this folder are sample implementations of a simple prototype, using the Dijkstra algorithm for finding the shortest path, in the simple_dijkstra_with_visualization file are also ideas on how to integrate reliability (and also some simple visuals).
## Other
The create_gtfs_db_full and create_script_gtfs_tables_db files contain database statements for importing the GTFS data into duck db (which is quite comfortable for querying the GTFS data, the structure is the same as in the files - with a separate table for routes, trips, stops, etc.).
