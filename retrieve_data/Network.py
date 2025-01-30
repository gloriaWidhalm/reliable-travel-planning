#!/usr/bin/env python
# coding: utf-8
import logging

# In[23]:


import duckdb
import pandas as pd
import numpy as np
from collections import defaultdict
from collections import defaultdict
import json

def get_data(date='2024-10-01', database_path='transport_data.db'):
    """Process transport data for a given date"""
    # Connect to the database
    logging.info(f"Getting data for date {date}, from database {database_path}")
    connection = duckdb.connect(database_path, read_only=False)
    
    weekday = pd.to_datetime(date).weekday() + 1
    
    query = f""" 
    SELECT *
    FROM services 
    WHERE PRODUCT_ID='Zug' 
    AND ARRIVAL_PREDICTION_STATUS='REAL' 
    AND DEPARTURE_PREDICTION_STATUS='REAL'
    AND strftime('%w', OPERATING_DAY) = '{weekday}'"""
    
    df_Zug = connection.execute(query).df()
    
    df_Zug = df_Zug.sort_values('ARRIVAL_PREDICTION')
    df_Zug['duplicate_number'] = df_Zug.groupby(['OPERATING_DAY', 'TRIP_IDENTIFIER', 'BPUIC']).cumcount() + 1
    
    def merge_predictions(df_Zug, base_date):
        unique_dates = sorted(df_Zug['OPERATING_DAY'].unique(), reverse=True)
        join_dates = [d for d in unique_dates if d != base_date]
        
        result_df = df_Zug[df_Zug['OPERATING_DAY'] == base_date].copy()
        
        base_date_str = pd.to_datetime(base_date).strftime('%Y-%m-%d')
        result_df = result_df.rename(columns={
            'DEPARTURE_PREDICTION': f'DEPARTURE_PREDICTION_{base_date_str}',
            'ARRIVAL_PREDICTION': f'ARRIVAL_PREDICTION_{base_date_str}'
        })
        
        for d in join_dates:
            temp_df = df_Zug[df_Zug['OPERATING_DAY'] == d][
                ['TRIP_IDENTIFIER', 'BPUIC', 'DEPARTURE_PREDICTION', 'ARRIVAL_PREDICTION', 'duplicate_number']
            ]
            
            date_str = pd.to_datetime(d).strftime('%Y-%m-%d')
            temp_df = temp_df.rename(columns={
                'DEPARTURE_PREDICTION': f'DEPARTURE_PREDICTION_{date_str}',
                'ARRIVAL_PREDICTION': f'ARRIVAL_PREDICTION_{date_str}'
            })
            
            result_df = result_df.merge(
                temp_df,
                on=['TRIP_IDENTIFIER', 'BPUIC', 'duplicate_number'],
                how='left'
            )
        
        return result_df
    
    result_df = merge_predictions(df_Zug, date)
    
    result_df['PLANNED_DEPARTURE'] = pd.to_datetime(result_df['DEPARTURE_TIME']).dt.time.apply(
        lambda x: x.hour * 60 + x.minute
    )
    result_df['PLANNED_ARRIVAL'] = pd.to_datetime(result_df['ARRIVAL_TIME']).dt.time.apply(
        lambda x: x.hour * 60 + x.minute
    )
    
    def convert_time_columns(df):
        prediction_columns = [col for col in df.columns if 'PREDICTION' in col and '_202' in col]
        for col in prediction_columns:
            df[col] = df[col].dt.hour * 60 + df[col].dt.minute
        return df
    
    result_df = convert_time_columns(result_df)
    
    connection.close()
    return result_df


def process_route_data(result_df, start_time=700, end_time=880, start_stop=8503000):
    """
    Process route data and generate dynamic route graph - all in one function
    
    Parameters:
    result_df (pd.DataFrame): Input DataFrame with route information
    start_time (int): Start time for both filtering and graph generation
    end_time (int): End time for filtering
    start_stop (int): Starting stop ID (default: 8503000)
    
    Returns:
    dict: Generated route graph
    """
    logging.info(f"Processing route data")
    logging.debug(f"Start time: {start_time}, End time: {end_time}, Start stop: {start_stop}")
    #logging.debug(f"Data: {result_df}")
    from collections import defaultdict
    import json
    import numpy as np
    import pandas as pd
    
    class TupleEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, tuple):
                return {'__tuple': True, 'items': obj}
            if isinstance(obj, (np.int64, np.int32)):
                return int(obj)
            return super(TupleEncoder, self).default(obj)
    
    def get_prediction_columns(df):
        prediction_columns = []
        for col in df.columns:
            if 'PREDICTION' in col and '_202' in col:
                prediction_columns.append(col)
        
        paired_columns = []
        for i in range(0, len(prediction_columns), 2):
            if i + 1 < len(prediction_columns):
                dep_col = prediction_columns[i]
                arr_col = prediction_columns[i + 1]
                paired_columns.append((dep_col, arr_col))
        logging.debug(f"Paired columns: {paired_columns}")
        return paired_columns
    
    # Filter and sort data
    mask = (result_df['PLANNED_ARRIVAL'] >= start_time) & (result_df['PLANNED_DEPARTURE'] <= end_time)
    df_filtered = result_df[mask]
    logging.debug("Filtering data")
    logging.debug(df_filtered)
    data = df_filtered.sort_values(['TRIP_IDENTIFIER', 'PLANNED_ARRIVAL'])
    
    # Initialize graph
    graph = defaultdict(list)
    prediction_pairs = get_prediction_columns(data)
    
    def get_predictions_for_transition(from_stop_data, to_stop_data):
        predictions = []
        for dep_col, arr_col in prediction_pairs:
            departure = from_stop_data[dep_col]
            arrival = to_stop_data[arr_col]
            if pd.notna(departure) and pd.notna(arrival):
                predictions.append((int(departure), int(arrival)))
        return predictions if predictions else None
    
    def build_line_path(stop, arrival_time, trip_identifier, prev_departure=None):
        logging.debug(f"Building line path for stop {stop} at time {arrival_time}")
        next_stops = data[
            (data['TRIP_IDENTIFIER'] == trip_identifier) &
            (data['PLANNED_ARRIVAL'] > arrival_time)
        ].sort_values('PLANNED_ARRIVAL')
        
        transfers = data[
            (data['BPUIC'] == stop) &
            (data['PLANNED_ARRIVAL'] > arrival_time) &
            (data['TRIP_IDENTIFIER'] != trip_identifier)
        ].sort_values('PLANNED_ARRIVAL')

        logging.debug(f"Next stops for stop {stop}: {next_stops}")
        logging.debug(f"Transfers for stop {stop}: {transfers}")
        
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
            
            if predictions is not None:  # Only add transition if there are valid predictions
                transition = {
                    "from": stop,
                    "planned_departure": current_departure,
                    "to": next_stop,
                    "planned_arrival": next_arrival,
                    "trip_id": trip_identifier,
                    "actual_times": predictions
                }
                
                if transition not in graph[stop]:
                    graph[stop].append(transition)
                    build_line_path(next_stop, next_arrival, trip_identifier, current_departure)
        for _, transfer in transfers.iterrows():
            new_trip_identifier = transfer['TRIP_IDENTIFIER']
            new_arrival = int(transfer['PLANNED_ARRIVAL'])
            new_departure = int(transfer['PLANNED_DEPARTURE'])
            
            predictions = get_predictions_for_transition(transfer, transfer)
            
            if predictions is not None:  # Only add transition if there are valid predictions
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
    logging.debug(f"Data, looking for stop identifier {start_stop}")
    logging.debug(data['BPUIC'])
    # Process initial routes
    initial_routes = data[
        (data['BPUIC'] == start_stop) &
        (data['PLANNED_ARRIVAL'] >= start_time)
    ].sort_values('PLANNED_ARRIVAL')

    logging.debug("Initial routes")
    logging.debug(initial_routes)

    if not initial_routes.empty:
        initial_route = initial_routes.iloc[0]
        initial_trip_identifier = initial_route['TRIP_IDENTIFIER']
        initial_arrival = int(initial_route['PLANNED_ARRIVAL'])
        
        build_line_path(start_stop, initial_arrival, initial_trip_identifier)
    
    # Remove self-transitions
    for stop in graph:
        graph[stop] = [transition for transition in graph[stop] 
                      if transition['to'] != stop]
    
    # Convert defaultdict to regular dict and return
    return dict(graph)



if __name__ == "__main__":
    # Test retrieving graph data (with main, so it is not executed when the functions are imported)
    data=get_data(date='2024-10-01')
    graph=process_route_data(data,700,760,8503000)




