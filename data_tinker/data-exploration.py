# This file contains some data exploration steps to understand the swiss transport data better
# Documentation see: https://opentransportdata.swiss/en/cookbook/actual-data/
# Your token for this API is: eyJvcmciOiI2NDA2NTFhNTIyZmEwNTAwMDEyOWJiZTEiLCJpZCI6ImRlYTRkZGFmMzU1YzRjNmRhY2E0YTlmYmNiYTE0Nzc2IiwiaCI6Im11cm11cjEyOCJ9
import duckdb
import pandas as pd

# Connect to the database
connection = duckdb.connect("../transport_data.db", read_only=False)


query = f""" CREATE TABLE IF NOT EXISTS services AS SELECT * FROM '../data/delay_data/*.csv'"""
connection.execute(query)

r = connection.sql("DESCRIBE services")
#print(r)
#exit(0)

# Query the database
query = f""" SELECT count(*) FROM services WHERE PRODUKT_ID='Zug' AND AN_PROGNOSE_STATUS='REAL' AND AB_PROGNOSE_STATUS='REAL'"""
query = f""" SELECT HALTESTELLEN_NAME, ANKUNFTSZEIT, AN_PROGNOSE, ABFAHRTSZEIT, AB_PROGNOSE FROM services WHERE PRODUKT_ID='Zug' AND AN_PROGNOSE_STATUS='REAL' AND AB_PROGNOSE_STATUS='REAL' LIMIT 10"""
pd.set_option('display.max_columns', None)
query = f""" SELECT BETREIBER_NAME, HALTESTELLEN_NAME, COUNT(*) FROM services WHERE PRODUKT_ID='Zug' AND AN_PROGNOSE_STATUS='REAL' AND AB_PROGNOSE_STATUS='REAL' AND AN_PROGNOSE > try_strptime(ANKUNFTSZEIT, '%d.%m.%Y %H:%M') + INTERVAL 5 MINUTE GROUP BY BETREIBER_NAME, HALTESTELLEN_NAME ORDER BY 3 """
query = f""" SELECT HALTESTELLEN_NAME, COUNT(*) FROM services WHERE PRODUKT_ID='Zug' AND AN_PROGNOSE_STATUS='REAL' AND AB_PROGNOSE_STATUS='REAL' AND AN_PROGNOSE > try_strptime(ANKUNFTSZEIT, '%d.%m.%Y %H:%M') + INTERVAL 5 MINUTE GROUP BY HALTESTELLEN_NAME ORDER BY 2 DESC """
query = f""" 
SELECT DISTINCT HALTESTELLEN_NAME
FROM services 
--WHERE PRODUKT_ID='Zug' 
WHERE AN_PROGNOSE_STATUS='REAL' 
AND AB_PROGNOSE_STATUS='REAL' 
AND AN_PROGNOSE > try_strptime(ANKUNFTSZEIT, '%d.%m.%Y %H:%M') + INTERVAL 5 MINUTE 
AND LINIEN_ID = '534'
"""

# Get the number of entries that have a delay of more than 5 minutes
query = f""" 
SELECT count(*)
FROM services 
--WHERE PRODUKT_ID='Zug' 
WHERE AN_PROGNOSE_STATUS='REAL' 
AND AB_PROGNOSE_STATUS='REAL' 
AND AN_PROGNOSE > try_strptime(ANKUNFTSZEIT, '%d.%m.%Y %H:%M') + INTERVAL 5 MINUTE 
"""
query = f""" SELECT HALTESTELLEN_NAME, ANKUNFTSZEIT, AN_PROGNOSE, ABFAHRTSZEIT, AB_PROGNOSE FROM services WHERE PRODUKT_ID='Zug' AND AN_PROGNOSE_STATUS='REAL' AND AB_PROGNOSE_STATUS='REAL' LIMIT 10"""
result = connection.sql(query).df()

# Print the result
print("Entries with delays > 5 minutes:")
print(result)

# Get the number of entries that have a delay of more than 5 minutes
query = f""" 
SELECT count(*)
FROM services 
WHERE PRODUKT_ID='Zug' 
AND AN_PROGNOSE_STATUS='REAL' 
AND AB_PROGNOSE_STATUS='REAL' 
AND AN_PROGNOSE > try_strptime(ANKUNFTSZEIT, '%d.%m.%Y %H:%M') + INTERVAL 5 MINUTE 
"""
result = connection.sql(query).df()

# Print the result
print("Train entries with delays > 5 minutes:")
print(result)

# Get the average delay grouped by PRODUKT_ID
query = f""" 
SELECT avg(epoch((AN_PROGNOSE - try_strptime(ANKUNFTSZEIT, '%d.%m.%Y %H:%M')))) as avg_delay, PRODUKT_ID
FROM services 
WHERE AN_PROGNOSE_STATUS='REAL' 
AND AB_PROGNOSE_STATUS='REAL' 
GROUP BY PRODUKT_ID
"""
result = connection.sql(query).df()

# Print the result
print("Average delay grouped by PRODUKT_ID:")
print(result)

# Get the count of all entries
query = f""" 
SELECT count(*)
FROM services 
WHERE PRODUKT_ID='Zug'
"""
result = connection.sql(query).df()

# Print the result
print("count:")
print(result)

# Close the connection
connection.close()