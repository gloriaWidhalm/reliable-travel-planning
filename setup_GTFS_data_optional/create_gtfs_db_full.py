# This file is there to create a full GTFS database from the Swiss transport data (full in a sense of using all available data - based on the GTFS files and not filtered by specific criteria).
from create_script_gtfs_tables_db import create_tables

# Import the necessary libraries
import zipfile
import duckdb


def unzip_gtfs(path):
    # Unzip the GTFS file
    with zipfile.ZipFile(path, "r") as zip_ref:
        zip_ref.extractall("./data/gtfs/gtfs_files")


def create_schema(connection):
    # Create the schema
    create_tables(connection)  # has "IF NOT EXISTS" in the create_table queries
    # print db schema
    r = connection.sql("SHOW TABLES")
    print("Tables in the database:")
    print(r)


def load_data(connection):
    # Load the data into the database
    # The files are in a text file with csv format (semicolon separated)
    # List of files
    files_to_load = [
        "agency.txt",
        "calendar.txt",
        "calendar_dates.txt",
        "routes.txt",
        "stop_times.txt",
        "stops.txt",
        "trips.txt",
        "transfers.txt",
    ]

    # Load the data into the database
    for file in files_to_load:
        print(f"Loading {file} into the database")
        # use
        copy_query = f"COPY {file.split('.')[0]} FROM './data/gtfs/gtfs_files/{file}' (delimiter ',', header, quote '\"', escape '\"', null_padding true, ignore_errors)"
        connection.execute(copy_query)
        # Print the tables (count)
        r = connection.sql(f"SELECT count(*) FROM {file.split('.')[0]}")
        print(f"Number of entries in {file.split('.')[0]}: {r}")


# main
if __name__ == "__main__":
    # File path:
    gtfs_path = "../data/gtfs/gtfs_train.zip"

    file_name_suffix = gtfs_path.split("/")[-1].split(".")[0]

    # Unzip the GTFS file
    unzip_gtfs(gtfs_path)

    # Connect to the database
    connection = duckdb.connect(f"../data/{file_name_suffix}.db", read_only=False)

    # Create the schema
    create_schema(connection)

    # Load the data into the database
    load_data(connection)
