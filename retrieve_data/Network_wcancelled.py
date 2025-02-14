#!/usr/bin/env python
# coding: utf-8

# In[1]:


import logging
import duckdb
import pandas as pd
import numpy as np
from collections import defaultdict
from collections import defaultdict
import json

def get_data(date='2024-10-02', database_path='transport_data.db'):

    # Connect to the database
    connection = duckdb.connect(database_path, read_only=False)
    
    # Get weekday number (1-7) for the given date
    weekday = pd.to_datetime(date).weekday() + 1
    
    # Query to get regular train services with real arrival/departure predictions
    query = f""" 
    SELECT distinct *
    FROM services 
    WHERE PRODUCT_ID='Zug' 
    AND ARRIVAL_PREDICTION_STATUS='REAL' 
    AND DEPARTURE_PREDICTION_STATUS='REAL'
    AND strftime('%w', OPERATING_DAY) = '{weekday}'"""
    
    df_Zug = connection.execute(query).df()
    
    # Query to get cancelled train services for the same weekday
    query = f""" 
        SELECT *
        FROM services 
        WHERE PRODUCT_ID='Zug' 
        AND CANCELLED_TF=1
        AND strftime('%w', OPERATING_DAY) = '{weekday}'
        AND ARRIVAL_PREDICTION_STATUS='UNBEKANNT' """
        
    df_cancelled = connection.execute(query).df()
    # Set maximum delay (2880 minutes = 48 hours) for cancelled services
    df_cancelled['ARRIVAL_PREDICTION'] = 2880
    df_cancelled['DEPARTURE_PREDICTION'] = 2880
    
    # Convert time predictions to minutes since midnight
    df_Zug['ARRIVAL_PREDICTION'] = df_Zug['ARRIVAL_PREDICTION'].apply(lambda x: 
    (x.hour * 60 + x.minute) if pd.notnull(x) else np.nan)
    df_Zug['DEPARTURE_PREDICTION'] = df_Zug['DEPARTURE_PREDICTION'].apply(lambda x: 
        (x.hour * 60 + x.minute) if pd.notnull(x) else np.nan)
    
    # Process data for the specific date
    df_day = df_Zug[df_Zug['OPERATING_DAY']==date].copy()
    df_day.loc[:, 'minute'] = pd.to_datetime(df_day['ARRIVAL_TIME']).dt.time.apply(lambda x: x.hour * 60 + x.minute)
    df_cancelled['minute'] = pd.to_datetime(df_cancelled['ARRIVAL_TIME'], errors='coerce').apply(lambda x: x.hour * 60 + x.minute if pd.notnull(x) else None)
    
    # Merge cancelled services with regular services based on trip identifier, station ID, and minute
    df_cancelled = df_cancelled.merge(df_day[['TRIP_IDENTIFIER', 'BPUIC', 'minute']], 
                                    on=['TRIP_IDENTIFIER', 'BPUIC', 'minute'], 
                                    how='inner')
    
    # Combine regular and cancelled services
    df_Zug = pd.concat([df_Zug, df_cancelled], ignore_index=True)
    
    # Sort by arrival prediction and handle duplicate entries
    df_Zug = df_Zug.sort_values('ARRIVAL_PREDICTION')
    df_Zug['duplicate_number'] = df_Zug.groupby(['OPERATING_DAY', 'TRIP_IDENTIFIER', 'BPUIC']).cumcount() + 1
    
    def merge_predictions(df_Zug, base_date):
        """Merge predictions from different dates for the same services
        
        Args:
            df_Zug (pandas.DataFrame): DataFrame containing all services
            base_date (str): Reference date for comparison
            
        Returns:
            pandas.DataFrame: DataFrame with merged predictions from different dates
        """
        base_date = pd.to_datetime(base_date).date()
        df_Zug['OPERATING_DAY'] = pd.to_datetime(df_Zug['OPERATING_DAY']).dt.date
        
        # Get unique dates sorted in descending order
        unique_dates = sorted(df_Zug['OPERATING_DAY'].unique(), reverse=True)
        
        # Get data for the base date
        result_df = df_Zug[df_Zug['OPERATING_DAY'] == base_date].copy()
        
        base_date_str = base_date.strftime('%Y-%m-%d')
        other_dates = [d for d in unique_dates if d != base_date]
        
        # Merge predictions from other dates
        for d in other_dates:
            temp_df = df_Zug[df_Zug['OPERATING_DAY'] == d][
                ['TRIP_IDENTIFIER', 'BPUIC', 'DEPARTURE_PREDICTION', 
                 'ARRIVAL_PREDICTION',  'duplicate_number']
            ]
            
            date_str = d.strftime('%Y-%m-%d')
            # Rename columns to include the date
            temp_df = temp_df.rename(columns={
                'DEPARTURE_PREDICTION': f'DEPARTURE_PREDICTION_{date_str}',
                'ARRIVAL_PREDICTION': f'ARRIVAL_PREDICTION_{date_str}'
            })
            
            # Merge with the result DataFrame
            result_df = result_df.merge(
                temp_df,
                on=['TRIP_IDENTIFIER', 'BPUIC', 'duplicate_number'],
                how='left'
            )
        
        return result_df
    
    # Process predictions for all dates
    result_df = merge_predictions(df_Zug, date)
    
    # Convert planned times to minutes since midnight
    result_df['PLANNED_DEPARTURE'] = pd.to_datetime(result_df['DEPARTURE_TIME']).dt.time.apply(
        lambda x: x.hour * 60 + x.minute
    )
    result_df['PLANNED_ARRIVAL'] = pd.to_datetime(result_df['ARRIVAL_TIME']).dt.time.apply(
        lambda x: x.hour * 60 + x.minute
    )
    
    # Close database connection and return results
    connection.close()
    return result_df

def process_route_data(result_df, start_time=700, end_time=880, start_stop=8503000):
    """Process train route data to create a graph of possible transitions between stops
    
    Args:
        result_df (pandas.DataFrame): DataFrame containing train route information
        start_time (int): Start time in minutes since midnight (default: 700 = 11:40 AM)
        end_time (int): End time in minutes since midnight (default: 880 = 2:40 PM)
        start_stop (int): Starting station ID (default: 8503000)
        
    Returns:
        dict: Graph representation of possible transitions between stops
    """
    from collections import defaultdict
    import json
    import numpy as np
    import pandas as pd
    
    # Custom JSON encoder to handle tuples and numpy integers
    class TupleEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, tuple):
                return {'__tuple': True, 'items': obj}
            if isinstance(obj, (np.int64, np.int32)):
                return int(obj)
            return super(TupleEncoder, self).default(obj)
    
    def get_prediction_columns(df):
        """Extract and pair prediction columns from the DataFrame
        
        Finds columns containing both 'PREDICTION' and '_202' (year) in their names
        and pairs them as (departure_prediction, arrival_prediction)
        """
        prediction_columns = []
        for col in df.columns:
            if 'PREDICTION' in col and '_202' in col:
                prediction_columns.append(col)
        
        # Pair departure and arrival prediction columns
        paired_columns = []
        for i in range(0, len(prediction_columns), 2):
            if i + 1 < len(prediction_columns):
                dep_col = prediction_columns[i]
                arr_col = prediction_columns[i + 1]
                paired_columns.append((dep_col, arr_col))

        return paired_columns
    
    # Filter data for the specified time window
    mask = (result_df['PLANNED_ARRIVAL'] >= start_time) & (result_df['PLANNED_DEPARTURE'] <= end_time)
    df_filtered = result_df[mask]

    # Sort data by trip and planned arrival time
    data = df_filtered.sort_values(['TRIP_IDENTIFIER', 'PLANNED_ARRIVAL'])
    
    # Initialize graph structure and get prediction column pairs
    graph = defaultdict(list)
    prediction_pairs = get_prediction_columns(data)
    
    def get_predictions_for_transition(from_stop_data, to_stop_data):
        """Get all valid predictions for a transition between two stops
        
        Args:
            from_stop_data: DataFrame row for departure stop
            to_stop_data: DataFrame row for arrival stop
            
        Returns:
            list of tuples: (departure_time, arrival_time) or None if no valid predictions
        """
        predictions = []
        for dep_col, arr_col in prediction_pairs:
            departure = from_stop_data[dep_col]
            arrival = to_stop_data[arr_col]
            if pd.notna(departure) and pd.notna(arrival):
                predictions.append((int(departure), int(arrival)))
        return predictions if predictions else None
    
    def build_line_path(stop, arrival_time, trip_identifier, prev_departure=None):
        """Recursively build path through the network for a given line
        
        Processes both direct connections (next stops on the same line)
        and transfers (connections to other lines at the same station)
        
        Args:
            stop: Current station ID
            arrival_time: Arrival time at current stop
            trip_identifier: Current trip ID
            prev_departure: Previous departure time (optional)
        """
        # Find next stops on the same line
        next_stops = data[
            (data['TRIP_IDENTIFIER'] == trip_identifier) &
            (data['PLANNED_ARRIVAL'] > arrival_time)
        ].sort_values('PLANNED_ARRIVAL')
        
        # Find possible transfers at current station
        transfers = data[
            (data['BPUIC'] == stop) &
            (data['PLANNED_ARRIVAL'] > arrival_time) &
            (data['TRIP_IDENTIFIER'] != trip_identifier)
        ].sort_values('PLANNED_ARRIVAL')

        # Process next stops on the same line
        if not next_stops.empty:
            next_stop_data = next_stops.iloc[0]
            next_stop = next_stop_data['BPUIC']
            next_arrival = int(next_stop_data['PLANNED_ARRIVAL'])
            
            current_stop_data = data[
                (data['BPUIC'] == stop) & 
                (data['TRIP_IDENTIFIER'] == trip_identifier) &
                (data['PLANNED_ARRIVAL'] == arrival_time)
            ].iloc[0]
            
            current_departure = int(current_stop_data['PLANNED_DEPARTURE'])
            
            predictions = get_predictions_for_transition(current_stop_data, next_stop_data)
            
            # Add transition if valid predictions exist
            if predictions is not None:
                transition = {
                    "from": stop,
                    "planned_departure": current_departure,
                    "to": next_stop,
                    "planned_arrival": next_arrival,
                    # as a simplification, we use the line text instead of the trip identifier
                    # this is because we saw that the trip identifier sometimes changed though it was still the same train/line
                    "trip_id": trip_identifier,
                    "actual_times": predictions
                }
                
                if transition not in graph[stop]:
                    graph[stop].append(transition)
                    build_line_path(next_stop, next_arrival, trip_identifier, current_departure)

        # Process transfers at current station
        for _, transfer in transfers.iterrows():
            new_trip_identifier = transfer['TRIP_IDENTIFIER']
            new_arrival = int(transfer['PLANNED_ARRIVAL'])
            new_departure = int(transfer['PLANNED_DEPARTURE'])

            predictions = get_predictions_for_transition(transfer, transfer)
            
            if predictions is not None:
                transition = {
                    "from": stop,
                    "planned_departure": new_departure,
                    "to": stop,
                    "planned_arrival": new_arrival,
                    "trip_id": new_trip_identifier,
                    "actual_times": predictions
                }
                
                if transition not in graph[stop]:
                    graph[stop].append(transition)
                    build_line_path(stop, new_arrival, new_trip_identifier)

    # Find and process initial routes from the start station
    initial_routes = data[
        (data['BPUIC'] == start_stop) &
        (data['PLANNED_ARRIVAL'] >= start_time)
    ].sort_values('PLANNED_ARRIVAL')

    # Start building the graph from the first available route
    if not initial_routes.empty:
        initial_route = initial_routes.iloc[0]
        initial_trip_identifier = initial_route['TRIP_IDENTIFIER']
        initial_arrival = int(initial_route['PLANNED_ARRIVAL'])
        
        build_line_path(start_stop, initial_arrival, initial_trip_identifier)
    
    # Clean up the graph by removing self-transitions
    for stop in graph:
        graph[stop] = [transition for transition in graph[stop] 
                      if transition['to'] != stop]
    
    # Convert defaultdict to regular dict and return
    return dict(graph)



if __name__ == "__main__":
    # Test retrieving graph data (with main, so it is not executed when the functions are imported)
    data=get_data(date='2024-10-01')
    graph=process_route_data(data,700,760,8503000)


# In[ ]:




