#DAP 2024: A prototype for reliable travel planning - data exploration
#Documentation see: https://opentransportdata.swiss/en/cookbook/actual-data/
#Working with data from 01/05/2024 - 31/10/2024

import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Connect to the database
connection = duckdb.connect("transport_data.db", read_only=False)
connection.execute("SET threads = 8") #set threads as necessary according to one's PC

# Create a table if it doesn't exist
query = f""" CREATE TABLE IF NOT EXISTS services AS SELECT * FROM './data/*.csv'"""
connection.execute(query)

# Rename each column using ALTER TABLE RENAME COLUMN statements
column_renames = [
    ("BETRIEBSTAG", "OPERATING_DAY"),
    ("FAHRT_BEZEICHNER", "TRIP_IDENTIFIER"),
    ("BETREIBER_ID", "OPERATOR_ID"),
    ("BETREIBER_ABK", "OPERATOR_ABK"),
    ("BETREIBER_NAME", "OPERATOR_NAME"),
    ("PRODUKT_ID", "PRODUCT_ID"),
    ("LINIEN_ID", "LINE_ID"),
    ("LINIEN_TEXT", "LINE_TEXT"),
    ("UMLAUF_ID", "CYCLE_ID"),
    ("VERKEHRSMITTEL_TEXT", "TRANSPORT_MODE_TEXT"),
    ("ZUSATZFAHRT_TF", "ADDITIONAL_TRIP_TF"),
    ("FAELLT_AUS_TF", "CANCELLED_TF"),
    ("BPUIC", "BPUIC"),
    ("HALTESTELLEN_NAME", "STOP_NAME"),
    ("ANKUNFTSZEIT", "ARRIVAL_TIME"),
    ("AN_PROGNOSE", "ARRIVAL_PREDICTION"),
    ("AN_PROGNOSE_STATUS", "ARRIVAL_PREDICTION_STATUS"),
    ("ABFAHRTSZEIT", "DEPARTURE_TIME"),
    ("AB_PROGNOSE", "DEPARTURE_PREDICTION"),
    ("AB_PROGNOSE_STATUS", "DEPARTURE_PREDICTION_STATUS"),
    ("DURCHFAHRT_TF", "THROUGH_TF")
]

# Execute each rename query
for old_name, new_name in column_renames:
    query = f"ALTER TABLE services RENAME COLUMN {old_name} TO {new_name}"
    connection.execute(query)

#Get all unique values of PRODUCT_ID
query = """
SELECT DISTINCT PRODUCT_ID
FROM services
"""
unique_product_ids = connection.execute(query).df()
print("Unique values of PRODUCT_ID:")
print(unique_product_ids)
# Tram, Zahnradbahn, BUS, Zug, Bus, Metro, Schiff, None

# Concatenate 'BUS' and 'Bus' into one uniform value in PRODUCT_ID across the whole database
query = """
UPDATE services
SET PRODUCT_ID = 'Bus'
WHERE PRODUCT_ID IN ('BUS')
"""
connection.execute(query).df()

#Get the count for each unique PRODUCT_ID, along with the occurrences with delays greater than 5 minutes
query = """
SELECT 
    PRODUCT_ID,
    COUNT(*) AS total_count,
    SUM(
        CASE 
            WHEN ARRIVAL_PREDICTION_STATUS = 'REAL' 
            AND DEPARTURE_PREDICTION_STATUS = 'REAL'
            AND ARRIVAL_PREDICTION > try_strptime(ARRIVAL_TIME, '%d.%m.%Y %H:%M') + INTERVAL 5 MINUTE
            THEN 1
            ELSE 0
        END
    ) AS delay_count 
FROM services
GROUP BY PRODUCT_ID
ORDER BY PRODUCT_ID
"""
product_id_counts = connection.execute(query).df()
print("Count for each unique PRODUCT_ID, including delay > 5 minutes:")
print(product_id_counts)
df_product_id_counts = product_id_counts # Save  as a DataFrame
df_product_id_counts['delay_percentage'] = (df_product_id_counts['delay_count'] / df_product_id_counts['total_count']) * 100 #add percentage
print(df_product_id_counts)

# Query to compute max and average delay for each PRODUCT_ID (without the 5-minute filter)
query = """
SELECT 
    PRODUCT_ID,
    MAX(epoch(ARRIVAL_PREDICTION - try_strptime(ARRIVAL_TIME, '%d.%m.%Y %H:%M'))) AS max_delay,
    AVG(epoch(ARRIVAL_PREDICTION - try_strptime(ARRIVAL_TIME, '%d.%m.%Y %H:%M'))) AS avg_delay
FROM services
WHERE ARRIVAL_PREDICTION_STATUS = 'REAL'
AND DEPARTURE_PREDICTION_STATUS = 'REAL'
AND ARRIVAL_PREDICTION > try_strptime(ARRIVAL_TIME, '%d.%m.%Y %H:%M')
GROUP BY PRODUCT_ID
ORDER BY PRODUCT_ID
"""
delay_statistics = connection.execute(query).df()
print(delay_statistics)

# Query to get delay data for Bus and Zug with delays of size 5 mins and more
query = """
SELECT 
    PRODUCT_ID,
    epoch(ARRIVAL_PREDICTION - try_strptime(ARRIVAL_TIME, '%d.%m.%Y %H:%M')) AS delay_seconds
FROM services
WHERE PRODUCT_ID IN ('Bus', 'Zug')
AND ARRIVAL_PREDICTION_STATUS = 'REAL'
AND DEPARTURE_PREDICTION_STATUS = 'REAL'
AND ARRIVAL_PREDICTION > try_strptime(ARRIVAL_TIME, '%d.%m.%Y %H:%M') + INTERVAL 5 MINUTE
"""
df_delays = connection.execute(query).df()
print(df_delays)

# Plotting the distribution of delays for Bus and Zug with delays of any size 300-7200 seconds
bus_delays = df_delays[df_delays['PRODUCT_ID'] == 'Bus']['delay_seconds']
zug_delays = df_delays[df_delays['PRODUCT_ID'] == 'Zug']['delay_seconds']
bus_delays_sampled = bus_delays.iloc[::10]  # Take every 10th point for a faster plot
zug_delays_sampled = zug_delays.iloc[::10]  # Take every 10th point for a faster plot

# Set up the figure for the density plot
plt.figure(figsize=(10, 6))
# Density Plot
sns.kdeplot(bus_delays_sampled, color='blue', label='Bus', fill=True, alpha=0.3)
sns.kdeplot(zug_delays_sampled, color='red', label='Zug', fill=True, alpha=0.3)
plt.xlabel('Delay (seconds)')
plt.ylabel('Density')
plt.title('Density Plot of Delays for Bus (Blue) and Zug (Red)')
plt.legend(loc='upper right')
plt.xlim(300, 7200)
plt.savefig('density_plot_delays.png')  # Save the density plot
plt.close()  # Close the figure to free up memory

# Create a sub-database with only 'Zug' PRODUCT_ID (services_zug)
query = """
CREATE TABLE services_zug AS
SELECT *
FROM services
WHERE PRODUCT_ID = 'Zug'
"""
connection.execute(query)

# Investigate missing values in critical columns for services_zug
query = """
SELECT 
    COUNT(*) AS total_rows,
    SUM(CASE WHEN ARRIVAL_TIME IS NULL THEN 1 ELSE 0 END) AS missing_arrival_time,
    SUM(CASE WHEN ARRIVAL_PREDICTION IS NULL THEN 1 ELSE 0 END) AS missing_arrival_prediction,
    (SUM(CASE WHEN ARRIVAL_TIME IS NULL THEN 1 ELSE 0 END) / COUNT(*)) * 100 AS missing_arrival_time_percentage,
    (SUM(CASE WHEN ARRIVAL_PREDICTION IS NULL THEN 1 ELSE 0 END) / COUNT(*)) * 100 AS missing_arrival_prediction_percentage
FROM services_zug
"""
missing_values = connection.execute(query).df()

print("Missing values in critical columns:")
print(missing_values) #What should be done with missing values?

# Count the number of complete row duplicates for trains (services_zug)
query = """
SELECT COUNT(*) AS duplicate_count
FROM (
    SELECT *, COUNT(*) AS row_count
    FROM services_zug
    GROUP BY *
    HAVING COUNT(*) > 1
) AS duplicates;
"""
duplicate_count = connection.execute(query).df()
print("Number of complete row duplicates:")
print(duplicate_count)
#54 duplicates

#Deleting complete duplicates from services_zug table
columns_query = """
PRAGMA table_info('services_zug');
"""
columns_info = connection.execute(columns_query).df()
column_names = columns_info['name'].tolist() # Extract column names into a list
columns_str = ", ".join(column_names) # Create the column list for PARTITION BY dynamically
count_duplicates_query = f"""
WITH duplicates AS (
    SELECT ROWID, 
           ROW_NUMBER() OVER (PARTITION BY {columns_str}) AS row_num
    FROM services_zug
)
SELECT COUNT(*) AS duplicate_count
FROM duplicates
WHERE row_num > 1
"""
duplicate_count_df = connection.execute(count_duplicates_query).df()
duplicate_count = duplicate_count_df['duplicate_count'][0]

# Print number of duplicate rows identified
print(f"Number of duplicate rows identified: {duplicate_count}")
delete_query = f"""
WITH duplicates AS (
    SELECT ROWID, 
           ROW_NUMBER() OVER (PARTITION BY {columns_str}) AS row_num
    FROM services_zug
)
DELETE FROM services_zug
WHERE ROWID IN (
    SELECT ROWID
    FROM duplicates
    WHERE row_num > 1
)
"""
connection.execute(delete_query)

# Find the ten lines with the largest delays where they occurred >10 times for product ID 'Zug' (services_zug)
query = """
SELECT 
    LINE_ID,
    AVG(epoch(ARRIVAL_PREDICTION - try_strptime(ARRIVAL_TIME, '%d.%m.%Y %H:%M'))) AS avg_delay,
    COUNT(*) AS occurrences
FROM services_zug
WHERE ARRIVAL_PREDICTION_STATUS = 'REAL'
AND DEPARTURE_PREDICTION_STATUS = 'REAL'
GROUP BY LINE_ID
HAVING COUNT(*) > 10
ORDER BY avg_delay DESC
LIMIT 10 
"""
ten_largest_delay_lines = connection.execute(query).df()
print("Lines with the largest delays:")
print(ten_largest_delay_lines)
largest_delay_lines_df = pd.DataFrame(ten_largest_delay_lines)# Store data in a DataFrame

line_ids = largest_delay_lines_df['LINE_ID'].tolist()# Extract line IDs

# Fetch delay data for the selected lines
query = f"""
SELECT 
    LINE_ID,
    ARRIVAL_TIME,
    STOP_NAME,
    epoch(ARRIVAL_PREDICTION - try_strptime(ARRIVAL_TIME, '%d.%m.%Y %H:%M')) AS delay_seconds
FROM services_zug
WHERE LINE_ID IN ({', '.join(f"'{line_id}'" for line_id in line_ids)})
AND ARRIVAL_PREDICTION_STATUS = 'REAL'
AND DEPARTURE_PREDICTION_STATUS = 'REAL'
AND ARRIVAL_PREDICTION > try_strptime(ARRIVAL_TIME, '%d.%m.%Y %H:%M')
"""
delay_data = connection.execute(query).df()

# Plot histograms for each line's delays
for line_id in line_ids:
    line_data = delay_data[delay_data['LINE_ID'] == line_id]['delay_seconds']
    plt.figure(figsize=(10, 6))
    sns.histplot(line_data, bins=30, color='red', alpha=0.6)
    plt.xlabel('Delay (seconds)')
    plt.ylabel('Frequency')
    plt.title(f'Histogram of Delays for Line {line_id}')
    plt.savefig(f'histogram_delay_line_{line_id}.png')  # Save each histogram
    plt.close()  # Close the figure to free up memory

# Descriptive statistics for the delays of the three lines
descriptive_stats = delay_data.groupby('LINE_ID').agg(
    min_delay=('delay_seconds', 'min'),
    max_delay=('delay_seconds', 'max'),
    average_delay=('delay_seconds', 'mean'),
    cumulative_delay=('delay_seconds', 'sum'),
    median_delay=('delay_seconds', 'median'),
    occurrences=('delay_seconds', 'count')
)

# Print the descriptive statistics
print("Descriptive statistics for the delays:")
print(descriptive_stats)
# Store descriptive statistics in a DataFrame and save to CSV
descriptive_stats_df = pd.DataFrame(descriptive_stats)
descriptive_stats_df.to_csv('descriptive_statistics_delays.csv')

# Fetch delay data for operators
query = """
SELECT 
    OPERATOR_ID,
    epoch(ARRIVAL_PREDICTION - try_strptime(ARRIVAL_TIME, '%d.%m.%Y %H:%M')) AS delay_seconds
FROM services_zug
WHERE ARRIVAL_PREDICTION_STATUS = 'REAL'
AND DEPARTURE_PREDICTION_STATUS = 'REAL'
AND ARRIVAL_PREDICTION > try_strptime(ARRIVAL_TIME, '%d.%m.%Y %H:%M')
"""
operator_delay_data = connection.execute(query).df()

# Create box plots for delays grouped by LINE_ID and OPERATOR_ID to assess variability
#plt.figure(figsize=(12, 8))
#sns.boxplot(x='LINE_ID', y='delay_seconds', data=delay_data)
#plt.xlabel('Line ID')
#plt.ylabel('Delay (seconds)')
#plt.title('Box Plot of Delays Grouped by Line ID')
#plt.savefig('boxplot_delays_by_line_id.png')
#plt.close()

# Box plot (with x-axis labels rotated)
plt.figure(figsize=(12, 8))
sns.boxplot(x='OPERATOR_ID', y='delay_seconds', data=operator_delay_data)
plt.xlabel('Operator ID')
plt.ylabel('Delay (seconds)')
plt.title('Box Plot of Delays Grouped by Operator ID')
plt.xticks(rotation=90)  # Rotate x-axis labels by 90 degrees
plt.tight_layout()
plt.savefig('boxplot_delays_by_operator_id.png')
plt.close()

# Create a DataFrame with average and median delay for each operator
delay_stats = operator_delay_data.groupby('OPERATOR_ID')['delay_seconds'].agg(
    average_delay='mean',
    median_delay='median'
).reset_index()
delay_stats.to_csv('operator_delay_statistics.csv', index=False) # Save the statistics

# Find the top 5 operators with the largest median delay
top_5_median_delay = delay_stats.nlargest(5, 'median_delay')
print("Top 5 operators with the largest median delay:")
for _, row in top_5_median_delay.iterrows():
    print(f"Operator ID: {row['OPERATOR_ID']}, Median Delay: {row['median_delay']} seconds")

# Find the top 5 operators with the largest average delay
top_5_average_delay = delay_stats.nlargest(5, 'average_delay')
print("\nTop 5 operators with the largest average delay:")
for _, row in top_5_average_delay.iterrows():
    print(f"Operator ID: {row['OPERATOR_ID']}, Average Delay: {row['average_delay']} seconds")

#TIME SERIES ANALYSIS
# Convert ARRIVAL_TIME to datetime and extract useful components
delay_data['ARRIVAL_TIME'] = pd.to_datetime(delay_data['ARRIVAL_TIME'], format='%d.%m.%Y %H:%M')
delay_data['hour'] = delay_data['ARRIVAL_TIME'].dt.hour
delay_data['day_of_week'] = delay_data['ARRIVAL_TIME'].dt.day_name()
delay_data['month'] = delay_data['ARRIVAL_TIME'].dt.month

# Time Series Analysis: Average delay by hour of the day
avg_delay_by_hour = delay_data.groupby('hour')['delay_seconds'].mean()
plt.figure(figsize=(10, 6))
plt.plot(avg_delay_by_hour.index, avg_delay_by_hour.values, marker='o')
plt.xlabel('Hour of the Day')
plt.ylabel('Average Delay (seconds)')
plt.title('Average Delay by Hour of the Day')
plt.grid(True)
plt.savefig('avg_delay_by_hour.png')
plt.close()

# Time Series Analysis: Average delay by day of the week
avg_delay_by_day = delay_data.groupby('day_of_week')['delay_seconds'].mean()
plt.figure(figsize=(10, 6))
plt.plot(avg_delay_by_day.index, avg_delay_by_day.values, marker='o')
plt.xlabel('Day of the Week')
plt.ylabel('Average Delay (seconds)')
plt.title('Average Delay by Day of the Week')
plt.xticks(rotation=45)
plt.grid(True)
plt.savefig('avg_delay_by_day.png')
plt.close()

# Time Series Analysis: Average delay by month
avg_delay_by_month = delay_data.groupby('month')['delay_seconds'].mean()
plt.figure(figsize=(10, 6))
plt.plot(avg_delay_by_month.index, avg_delay_by_month.values, marker='o')
plt.xlabel('Month')
plt.ylabel('Average Delay (seconds)')
plt.title('Average Delay by Month')
plt.grid(True)
plt.savefig('avg_delay_by_month.png')
plt.close()

# Identify which stops or stations (STOP_NAME) tend to have the most significant delays
avg_delay_by_stop = delay_data.groupby('STOP_NAME')['delay_seconds'].mean().sort_values(ascending=False)
print("Stops with the most significant delays:")
print(avg_delay_by_stop.head(10))

# Plot the top 10 stops with the most significant delays
plt.figure(figsize=(12, 8))
bars = avg_delay_by_stop.head(10).plot(kind='bar', color='red', alpha=0.7)
plt.xlabel('Stop Name')
plt.ylabel('Average Delay (seconds)')
plt.title('Top 10 Stops with the Most Significant Delays')
plt.xticks(rotation=75)
plt.grid(True)
for bar in bars.patches:
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{bar.get_height():.2f}', ha='center', va='bottom')
plt.tight_layout()
plt.savefig('top_10_stops_with_most_delays.png')
plt.close()

#OUTLIER DETECTION - regarding the delay using boxplot and IQR method
plt.figure(figsize=(12, 8))
sns.boxplot(x=delay_data['delay_seconds'])
plt.xlabel('Delay (seconds)')
plt.title('Box Plot of Delays to Detect Outliers')
plt.savefig('boxplot_delays_outliers.png')
plt.close()

# Use the IQR method to detect outliers
Q1 = delay_data['delay_seconds'].quantile(0.25)
Q3 = delay_data['delay_seconds'].quantile(0.75)
IQR = Q3 - Q1
outliers = delay_data[(delay_data['delay_seconds'] < (Q1 - 1.5 * IQR)) | (delay_data['delay_seconds'] > (Q3 + 1.5 * IQR))]
print("Number of outliers detected:", len(outliers))
print("Outliers:")
print(outliers)

# Delete outliers from zug_services table
outlier_ids = outliers['LINE_ID'].unique()
query = f"""
DELETE FROM zug_services
WHERE LINE_ID IN ({', '.join(f"'{line_id}'" for line_id in outlier_ids)})
AND epoch(ARRIVAL_PREDICTION - try_strptime(ARRIVAL_TIME, '%d.%m.%Y %H:%M')) IN ({', '.join(str(delay) for delay in outliers['delay_seconds'].tolist())})
"""
cursor = connection.execute(query)
deleted_rows = cursor.rowcount
print(f"Number of rows deleted from zug_services: {deleted_rows}")

connection.close()