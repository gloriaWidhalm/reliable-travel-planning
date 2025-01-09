# Create the tables

create_agency = f""" CREATE TABLE IF NOT EXISTS agency (
    agency_id VARCHAR NOT NULL, --PRIMARY KEY,
    agency_name VARCHAR NOT NULL,
    agency_url VARCHAR NOT NULL,
    agency_timezone VARCHAR NOT NULL,
    agency_lang VARCHAR,
    agency_phone VARCHAR
);"""

create_route = f"""
CREATE TABLE IF NOT EXISTS routes (
    route_id VARCHAR, --PRIMARY KEY,
    agency_id VARCHAR,
    route_short_name VARCHAR,
    route_long_name VARCHAR,
    route_desc VARCHAR,
    route_type INTEGER,
    --route_url VARCHAR,
    --route_color VARCHAR,
    --route_text_color VARCHAR,
    --FOREIGN KEY (agency_id) REFERENCES agency(agency_id)
); """

create_calendar = f""" CREATE TABLE IF NOT EXISTS calendar (
    service_id VARCHAR NOT NULL, --PRIMARY KEY,
    monday INTEGER NOT NULL,
    tuesday INTEGER NOT NULL,
    wednesday INTEGER NOT NULL,
    thursday INTEGER NOT NULL,
    friday INTEGER NOT NULL,
    saturday INTEGER NOT NULL,
    sunday INTEGER NOT NULL,
    start_date VARCHAR NOT NULL,
    end_date VARCHAR NOT NULL
);"""

create_calendar_dates = f""" CREATE TABLE IF NOT EXISTS calendar_dates (
    service_id VARCHAR NOT NULL,
    date VARCHAR NOT NULL,
    exception_type INTEGER NOT NULL,
    --PRIMARY KEY (service_id, date),
    --FOREIGN KEY (service_id) REFERENCES calendar(service_id)
);"""

create_shape = f""" CREATE TABLE IF NOT EXISTS shapes (
    shape_id VARCHAR NOT NULL,-- PRIMARY KEY,
    shape_pt_lat DECIMAL(9,6) NOT NULL,
    shape_pt_lon DECIMAL(9,6) NOT NULL,
    shape_pt_sequence INTEGER NOT NULL,
    shape_dist_traveled DECIMAL(9,6)
);"""

create_trip = f""" CREATE TABLE IF NOT EXISTS trips (
    route_id VARCHAR NOT NULL,
    service_id VARCHAR NOT NULL,
    trip_id VARCHAR NOT NULL,-- PRIMARY KEY,
    trip_headsign VARCHAR,
    trip_short_name VARCHAR,
    direction_id INTEGER,
    block_id VARCHAR,
    -- shape_id VARCHAR,
    --FOREIGN KEY (route_id) REFERENCES routes(route_id),
    --FOREIGN KEY (service_id) REFERENCES calendar(service_id),
    --FOREIGN KEY (shape_id) REFERENCES shape(shape_id)
);"""

create_stop = f""" CREATE TABLE IF NOT EXISTS stops (
    stop_id VARCHAR NOT NULL,-- PRIMARY KEY,
    stop_code VARCHAR,
    stop_name VARCHAR NOT NULL,
    stop_desc VARCHAR,
    stop_lat DECIMAL(9,6) NOT NULL,
    stop_lon DECIMAL(9,6) NOT NULL,
    zone_id VARCHAR,
    stop_url VARCHAR,
    location_type INTEGER,
    parent_station VARCHAR,
    --FOREIGN KEY (parent_station) REFERENCES stops(stop_id)
); """

create_stop_time = f""" CREATE TABLE IF NOT EXISTS stop_times (
    trip_id VARCHAR NOT NULL,
    arrival_time VARCHAR,
    departure_time VARCHAR,
    stop_id VARCHAR NOT NULL,
    stop_sequence INTEGER NOT NULL,
    -- stop_headsign VARCHAR,
    pickup_type INTEGER,
    drop_off_type INTEGER,
    -- shape_dist_traveled DECIMAL(9,6),
    --PRIMARY KEY (trip_id, stop_sequence),
    --FOREIGN KEY (trip_id) REFERENCES trips(trip_id),
    --FOREIGN KEY (stop_id) REFERENCES stops(stop_id)
);"""

create_transfer = f"""CREATE TABLE IF NOT EXISTS transfers (
    from_stop_id VARCHAR NOT NULL,
    to_stop_id VARCHAR NOT NULL,
    transfer_type INTEGER NOT NULL,
    min_transfer_time INTEGER,
    --PRIMARY KEY (from_stop_id, to_stop_id),
    --FOREIGN KEY (from_stop_id) REFERENCES stops(stop_id),
    --FOREIGN KEY (to_stop_id) REFERENCES stops(stop_id)
); """

CREATE_TABLES = [create_agency, create_route, create_calendar, create_calendar_dates, create_trip, create_stop, create_stop_time, create_transfer]


def create_tables(connection, create_tables=CREATE_TABLES):
    for create_query in create_tables:
        connection.execute(create_query)
