import logging

import duckdb

from constants import LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL)

def setup_delay_data(db_connection, data_path, delete_old=False):
    """
    Set up the delay data (used as input for our input, building the graph data for the algorithm (our railway network))
    """
    logging.info(f"Setting up delay data from {data_path} in database {db_path}")

    # delete old data
    if delete_old:
        query = '''DROP TABLE IF EXISTS services'''
        db_connection.execute(query)
        logging.info("Table services deleted")

    # check if table exists
    query = '''SELECT * FROM services LIMIT 1'''
    try:
        db_connection.execute(query)
        logging.info("Table services already exists")
        return db_connection
    except:
        pass

    query = f""" CREATE TABLE IF NOT EXISTS services AS SELECT * FROM '{data_path}'"""
    db_connection.execute(query)
    logging.info("Table services created")
    return db_connection

def rename_columns_from_german_to_english(db_connection):

    # check if columns are already renamed
    query = '''SELECT * FROM services LIMIT 1'''
    columns = db_connection.execute(query).df().columns
    if 'OPERATING_DAY' in columns:
        logging.info("Columns already renamed")
        return
    # rename columns

    query = '''ALTER TABLE services
    RENAME COLUMN BETRIEBSTAG TO OPERATING_DAY;

    ALTER TABLE services
    RENAME COLUMN FAHRT_BEZEICHNER TO TRIP_IDENTIFIER;

    ALTER TABLE services
    RENAME COLUMN BETREIBER_ID TO OPERATOR_ID;

    ALTER TABLE services
    RENAME COLUMN BETREIBER_ABK TO OPERATOR_ABK;

    ALTER TABLE services
    RENAME COLUMN BETREIBER_NAME TO OPERATOR_NAME;

    ALTER TABLE services
    RENAME COLUMN PRODUKT_ID TO PRODUCT_ID;

    ALTER TABLE services
    RENAME COLUMN LINIEN_ID TO LINE_ID;

    ALTER TABLE services
    RENAME COLUMN LINIEN_TEXT TO LINE_TEXT;

    ALTER TABLE services
    RENAME COLUMN UMLAUF_ID TO CYCLE_ID;

    ALTER TABLE services
    RENAME COLUMN VERKEHRSMITTEL_TEXT TO TRANSPORT_MODE_TEXT;

    ALTER TABLE services
    RENAME COLUMN ZUSATZFAHRT_TF TO ADDITIONAL_TRIP_TF;

    ALTER TABLE services
    RENAME COLUMN FAELLT_AUS_TF TO CANCELLED_TF;

    ALTER TABLE services
    RENAME COLUMN BPUIC TO BPUIC;

    ALTER TABLE services
    RENAME COLUMN HALTESTELLEN_NAME TO STOP_NAME;

    ALTER TABLE services
    RENAME COLUMN ANKUNFTSZEIT TO ARRIVAL_TIME;

    ALTER TABLE services
    RENAME COLUMN AN_PROGNOSE TO ARRIVAL_PREDICTION;

    ALTER TABLE services
    RENAME COLUMN AN_PROGNOSE_STATUS TO ARRIVAL_PREDICTION_STATUS;

    ALTER TABLE services
    RENAME COLUMN ABFAHRTSZEIT TO DEPARTURE_TIME;

    ALTER TABLE services
    RENAME COLUMN AB_PROGNOSE TO DEPARTURE_PREDICTION;

    ALTER TABLE services
    RENAME COLUMN AB_PROGNOSE_STATUS TO DEPARTURE_PREDICTION_STATUS;

    ALTER TABLE services
    RENAME COLUMN DURCHFAHRT_TF TO THROUGH_TF; '''
    db_connection.execute(query).df()
    logging.info("Columns renamed")

def check_database_entries(db_connection):
    query = '''SELECT count(*), ARRIVAL_TIME FROM services group by ARRIVAL_TIME'''
    result_df = db_connection.execute(query).df()
    print(result_df)
def get_list_of_stop_identifiers_with_name(db_connection):
    query = '''SELECT DISTINCT BPUIC, STOP_NAME FROM services'''
    return db_connection.execute(query).df()

if __name__ == "__main__":
    # Connect to the database
    db_path = "../transport_data.db"
    db_connection = duckdb.connect(db_path, read_only=False)
    setup_delay_data(db_connection, '../data/delay_data/2024-*.csv', delete_old=True)

    rename_columns_from_german_to_english(db_connection)

    #stop_identifiers = get_list_of_stop_identifiers_with_name(db_connection)

    check_database_entries(db_connection)

