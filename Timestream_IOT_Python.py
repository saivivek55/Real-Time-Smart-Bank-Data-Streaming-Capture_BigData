#!/usr/bin/env python
# coding: utf-8

# # Timestream 

# In[1]:


import boto3
import pandas as pd
from io import StringIO
import time
import folium


# In[2]:


AWS_ACCESS_KEY = "xxxxx"
AWS_SECRET_KEY = "xxxx"
AWS_REGION = "xxxxx"


# In[3]:


# conect to timestream
timestream_client_query = boto3.client(
    "timestream-query",
    aws_access_key_id = AWS_ACCESS_KEY,
    aws_secret_access_key = AWS_SECRET_KEY,
    region_name = AWS_REGION,
)


# In[4]:


# conect to timestream
timestream_client_query = boto3.client(
    "timestream-query",
    aws_access_key_id = AWS_ACCESS_KEY,
    aws_secret_access_key = AWS_SECRET_KEY,
    region_name = AWS_REGION,
)


# In[5]:


df = pd.DataFrame()


# In[6]:


DATABASE_NAME = "demoThingDB"
TABLE_NAME = "demoThingTable"
HT_TTL_HOURS = 24
CT_TTL_DAYS = 7


# In[7]:


class Query(object):

    def __init__(self, client):
        self.client = client
        self.paginator = client.get_paginator('query')

    # See records ingested into this table so far
    SELECT_ALL = f"SELECT * FROM {DATABASE_NAME}.{TABLE_NAME}"

    def run_query(self, query_string):
        try:
            page_iterator = self.paginator.paginate(QueryString=query_string)
            for page in page_iterator:
                self._parse_query_result(page)
        except Exception as err:
            print("Exception while running query:", err)
        

    def _parse_query_result(self, query_result):
        column_info = query_result['ColumnInfo']
        for row in query_result['Rows']:
            d = self._parse_row(column_info, row)
            df.append(d)
            #print(d)

    def _parse_row(self, column_info, row):
        data = row['Data']
        row_output = []
        for j in range(len(data)):
            info = column_info[j]
            datum = data[j]
            row_output.append(self._parse_datum(info, datum))

        return "{%s}" % str(row_output)

    def _parse_datum(self, info, datum):
        if datum.get('NullValue', False):
            return "%s=NULL" % info['Name'],

        column_type = info['Type']

        # If the column is of TimeSeries Type
        if 'TimeSeriesMeasureValueColumnInfo' in column_type:
            return self._parse_time_series(info, datum)

        # If the column is of Array Type
        elif 'ArrayColumnInfo' in column_type:
            array_values = datum['ArrayValue']
            return "%s=%s" % (info['Name'], self._parse_array(info['Type']['ArrayColumnInfo'], array_values))

        # If the column is of Row Type
        elif 'RowColumnInfo' in column_type:
            row_column_info = info['Type']['RowColumnInfo']
            row_values = datum['RowValue']
            return self._parse_row(row_column_info, row_values)

        # If the column is of Scalar Type
        else:
            return self._parse_column_name(info) + datum['ScalarValue']

    def _parse_time_series(self, info, datum):
        time_series_output = []
        for data_point in datum['TimeSeriesValue']:
            time_series_output.append("{time=%s, value=%s}"
                                      % (data_point['Time'],
                                         self._parse_datum(info['Type']['TimeSeriesMeasureValueColumnInfo'],
                                                           data_point['Value'])))
        return "[%s]" % str(time_series_output)

    def _parse_array(self, array_column_info, array_values):
        array_output = []
        for datum in array_values:
            array_output.append(self._parse_datum(array_column_info, datum))

        return "[%s]" % str(array_output)

    def run_query_with_multiple_pages(self, limit):
        query_with_limit = self.SELECT_ALL + " LIMIT " + str(limit)
        print("Starting query with multiple pages : " + query_with_limit)
        self.run_query(query_with_limit)

    def cancel_query(self):
        print("Starting query: " + self.SELECT_ALL)
        result = self.client.query(QueryString=self.SELECT_ALL)
        print("Cancelling query: " + self.SELECT_ALL)
        try:
            self.client.cancel_query(QueryId=result['QueryId'])
            print("Query has been successfully cancelled")
        except Exception as err:
            print("Cancelling query failed:", err)

    @staticmethod
    def _parse_column_name(info):
        if 'Name' in info:
            return info['Name'] + "="
        else:
            return ""


# # Decryption

# In[8]:


from cryptography.fernet import Fernet


# In[9]:


# Function to decrypt data
def decrypt_data(encrypted_data):
    decrypted_data = float(cipher_suite.decrypt(encrypted_data).decode())
    return decrypted_data


# In[10]:


query = Query(timestream_client_query)


# In[11]:


df = []
QUERY_1 = f"""
        SELECT measure_value::double
        FROM {DATABASE_NAME}.{TABLE_NAME} where measure_name = 'lat'
        """


# In[12]:


query.run_query(QUERY_1)


# In[13]:


# Extract numerical values from each string
latitude = []
for value in df:
    # Extract the numerical part of the string and remove extra characters
    numerical_part = value.split("::double=")[-1]
    numerical_part = numerical_part[:len(numerical_part)-3]
    # Convert the numerical part to a float and append to the list
    latitude.append(float(numerical_part))


# In[14]:


df = []
QUERY_1 = f"""
        SELECT measure_value::double
        FROM {DATABASE_NAME}.{TABLE_NAME} where measure_name = 'lon'
        """
query.run_query(QUERY_1)


# In[15]:


# Extract numerical values from each string
longitude = []
for value in df:
    # Extract the numerical part of the string and remove extra characters
    numerical_part = value.split("::double=")[-1]
    numerical_part = numerical_part[:len(numerical_part)-3]
    # Convert the numerical part to a float and append to the list
    longitude.append(float(numerical_part))


# In[16]:


len(longitude)


# In[17]:


df = []
QUERY_1 = f"""
        SELECT measure_value::double
        FROM {DATABASE_NAME}.{TABLE_NAME} where measure_name = 'alt'
        """
query.run_query(QUERY_1)


# In[18]:


# Extract numerical values from each string
altitude = []
for value in df:
    # Extract the numerical part of the string and remove extra characters
    numerical_part = value.split("::double=")[-1]
    numerical_part = numerical_part[:len(numerical_part)-3]
    # Convert the numerical part to a float and append to the list
    altitude.append(float(numerical_part))


# In[19]:


len(altitude)


# In[20]:


# Find the maximum length among the lists
max_length = max(len(latitude), len(longitude), len(altitude))

# Fill the lists with NaNs to make them equal length
latitude += [float('nan')] * (max_length - len(latitude))
longitude += [float('nan')] * (max_length - len(longitude))
altitude += [float('nan')] * (max_length - len(altitude))


# In[21]:


location = pd.DataFrame()
location['latitude'] = latitude
location['longitude'] = longitude
location['altitude'] = altitude


# In[22]:


location.head()


# In[23]:


location.dropna(inplace=True)


# In[24]:


location.head()


# In[ ]:





# In[25]:


import requests
import pandas as pd

# script for returning elevation from lat, long, based on open elevation data
# which in turn is based on SRTM
def get_elevation(lat, long):
    query = ('https://api.open-elevation.com/api/v1/lookup'
             f'?locations={lat},{long}')
    r = requests.get(query).json()  # json object, various ways you can extract value
    # one approach is to use pandas json functionality:
    elevation = pd.io.json.json_normalize(r, 'results')['elevation'].values[0]
    return elevation


# # Ramdom Sampling

# In[26]:


# importing geopy library
from geopy.geocoders import Nominatim
# calling the Nominatim tool
loc = Nominatim(user_agent="GetLoc")
 
# entering the location name
getLoc = loc.geocode("San Jose")
lat = getLoc.latitude
long = getLoc.longitude


# In[27]:


n = 50
sampled_df = location.sample(n)


# In[28]:


sampled_df.head()


# In[29]:


counts = sampled_df.groupby(['latitude', 'longitude']).size()

# Get the unique latitude and longitude with the highest count
max_count_value = counts.idxmax()
max_count = counts.max()
print(max_count_value)
max_latitude, max_longitude = max_count_value


# In[30]:


max_altitude = get_elevation(max_latitude, max_longitude)


# In[31]:


max_altitude


# In[32]:


t = []
hl = 0.2
hlt = 0.2
ha = 100 
for index, row in sampled_df.iterrows():
    dif_l = row['latitude'] - max_latitude
    dif_long = row['longitude'] - max_longitude
    dif_alt = row['altitude'] - max_altitude
    if (dif_l<hl) and (dif_long<hlt) and (dif_alt<ha):
        t.append("Approved")
    else:
        t.append("Fake transaction")


# In[33]:


sampled_df['Detail'] = t


# In[34]:


sampled_df.head()


# In[35]:


# Create a map centered around the mean latitude and longitude
map_center = [sampled_df['latitude'].mean(), sampled_df['longitude'].mean()]
mymap = folium.Map(location=map_center, zoom_start=5)

# Add markers to the map for each latitude and longitude pair
for index, row in sampled_df.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=f'Type: {row["Detail"]}',
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(mymap)


# In[36]:


mymap


# # Reservoir sampling 

# In[37]:


import random


# In[38]:


def reservoir_sampling(df, k):
    # Initialize an empty list to store the sampled rows
    sample = []
    
    # Iterate through each row in the DataFrame
    for i, row in df.iterrows():
        # If the length of the sample is less than k, add the row to the sample
        if len(sample) < k:
            sample.append(row)
        else:
            # Generate a random index j between 0 and i (inclusive)
            j = random.randint(0, i)
            # If j is less than k, replace the j-th element of the sample with the current row
            if j < k:
                sample[j] = row
    
    # Convert the list of sampled rows into a DataFrame
    sampled_dfr = pd.DataFrame(sample)
    
    return sampled_dfr


# In[39]:


# Set the size of the sample
sample_size = 50

# Perform reservoir sampling
sampled_dfr = reservoir_sampling(location, sample_size)


# In[40]:


counts = sampled_dfr.groupby(['latitude', 'longitude']).size()

# Get the unique latitude and longitude with the highest count
max_count_value = counts.idxmax()
max_count = counts.max()
print(max_count_value)
max_latitude, max_longitude = max_count_value
max_altitude = get_elevation(max_latitude, max_longitude)


# In[41]:


max_count


# In[42]:


tr = []
hl = 0.2
hlt = 0.2
ha = 100 
# distance between 2 latitude/longitude = 69miles
for index, row in sampled_dfr.iterrows():
    dif_l = row['latitude'] - max_latitude
    dif_long = row['longitude'] - max_longitude
    dif_alt = row['altitude'] - max_altitude
    if (dif_l<hl) and (dif_long<hlt) and (dif_alt<ha):
        tr.append("Approved")
    else:
        tr.append("Fake transaction")


# In[43]:


sampled_dfr['Detail'] = tr


# In[44]:


sampled_dfr.head()


# In[45]:


sampled_dfr.to_csv('sample.csv', index=False)


# In[46]:


# Create a map centered around the mean latitude and longitude
map_center = [sampled_dfr['latitude'].mean(), sampled_dfr['longitude'].mean()]
mymap = folium.Map(location=map_center, zoom_start=5)

# Add markers to the map for each latitude and longitude pair
for index, row in sampled_dfr.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=f'Type: {row["Detail"]}',
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(mymap)


# In[47]:


mymap


# # Bloomfilter

# In[181]:


import hashlib
import pandas as pd
import time
from pybloomfilter import BloomFilter


# In[182]:


testdf = location


# In[183]:


def funlatitude():
    query = Query(timestream_client_query)
    df = []
    QUERY_1 = f"""
                SELECT measure_value::double
                FROM {DATABASE_NAME}.{TABLE_NAME} where measure_name = 'lat' ORDER BY time DESC LIMIT 1
                """
    query.run_query(QUERY_1)
    latitude = 0
    for value in df:
        # Extract the numerical part of the string and remove extra characters
        numerical_part = value.split("::double=")[-1]
        numerical_part = numerical_part[:len(numerical_part)-3]
        # Convert the numerical part to a float and append to the list
        latitude = float(numerical_part)
    return latitude


# In[184]:


def funlongitude():
    query = Query(timestream_client_query)
    df = []
    QUERY_1 = f"""
            SELECT measure_value::double
            FROM {DATABASE_NAME}.{TABLE_NAME} where measure_name = 'lon' ORDER BY time DESC LIMIT 1
            """
    query.run_query(QUERY_1)
    # Extract numerical values from each string
    longitude = 0
    for value in df:
        # Extract the numerical part of the string and remove extra characters
        numerical_part = value.split("::double=")[-1]
        numerical_part = numerical_part[:len(numerical_part)-3]
        # Convert the numerical part to a float and append to the list
        longitude = float(numerical_part)
    return longitude


# In[185]:


def funaltitude():
    query = Query(timestream_client_query)
    df = []
    QUERY_1 = f"""
            SELECT measure_value::double
            FROM {DATABASE_NAME}.{TABLE_NAME} where measure_name = 'alt' ORDER BY time DESC LIMIT 1
            """
    query.run_query(QUERY_1)
    # Extract numerical values from each string
    altitude = 0
    for value in df:
        # Extract the numerical part of the string and remove extra characters
        numerical_part = value.split("::double=")[-1]
        numerical_part = numerical_part[:len(numerical_part)-3]
        # Convert the numerical part to a float and append to the list
        altitude = float(numerical_part)
    return altitude


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[186]:


def loc(latitude,longitude,altitude):
    # Find the maximum length among the lists
    location = pd.DataFrame()
    location['latitude'] = latitude
    location['longitude'] = longitude
    location['altitude'] = altitude
    location.dropna(inplace=True)
    return location


# In[187]:


traindf = sampled_dfr[sampled_dfr['Detail'] == 'Approved']


# In[188]:


traindf.drop(columns=['Detail']).head()


# In[189]:


# Function to hash the concatenated string of latitude, longitude, and altitude
def hash_coordinates(lat, lon, alt):
    return hashlib.sha256(f"{lat}{lon}{alt}".encode()).hexdigest()


# In[190]:


# Create a Bloom filter
filter_capacity = 1000  # Set an appropriate capacity for your dataset
error_rate = 0.001  # Set an appropriate error rate
bloom_filter = BloomFilter(filter_capacity, error_rate, 'filter.bloom')


# In[191]:


# Insert data into Bloom filter
for index, row in traindf.iterrows():
    coordinates_hash = hash_coordinates(row['latitude'], row['longitude'], row['altitude'])
    bloom_filter.add(coordinates_hash)


# In[192]:


def blfliter(latitude,longitude,altitude):    
    test_hash = hash_coordinates(latitude, longitude, altitude)
    if test_hash in bloom_filter:
        print("is possibly in the dataset.")
        return (1)
    else:
        print(index,"is not in the dataset.")
        return(0)


# In[193]:


try:
    with open("example.txt", 'w') as file:
        print("done")
except Exception as e:
    print(f"An error occurred: {e}")


# In[194]:


def transfer(data):
    try:
        with open("example.txt", 'a') as file:
            file.write(data)
    except Exception as e:
        print(f"An error occurred: {e}") 


# In[197]:


id = 1
try:
    with open(file_name, 'w') as file:
        file.write(data)
except Exception as e:
    print(f"An error occurred: {e}")
while(True):
    lat = funlatitude()
    query = Query(timestream_client_query)
    df = []
    QUERY_1 = f"""
                SELECT measure_value::double
                FROM {DATABASE_NAME}.{TABLE_NAME} where measure_name = 'lat' ORDER BY time DESC LIMIT 1
                """
    query.run_query(QUERY_1)
    latitude = 0
    for value in df:
        # Extract the numerical part of the string and remove extra characters
        numerical_part = value.split("::double=")[-1]
        numerical_part = numerical_part[:len(numerical_part)-3]
        # Convert the numerical part to a float and append to the list
        latitude = float(numerical_part)

        
        
    query = Query(timestream_client_query)
    df = []
    QUERY_1 = f"""
            SELECT measure_value::double
            FROM {DATABASE_NAME}.{TABLE_NAME} where measure_name = 'lon' ORDER BY time DESC LIMIT 1
            """
    query.run_query(QUERY_1)
    # Extract numerical values from each string
    longitude = 0
    for value in df:
        # Extract the numerical part of the string and remove extra characters
        numerical_part = value.split("::double=")[-1]
        numerical_part = numerical_part[:len(numerical_part)-3]
        # Convert the numerical part to a float and append to the list
        longitude = float(numerical_part)

    
    query = Query(timestream_client_query)
    df = []
    QUERY_1 = f"""
            SELECT measure_value::double
            FROM {DATABASE_NAME}.{TABLE_NAME} where measure_name = 'alt' ORDER BY time DESC LIMIT 1
            """
    query.run_query(QUERY_1)
    # Extract numerical values from each string
    altitude = 0
    for value in df:
        # Extract the numerical part of the string and remove extra characters
        numerical_part = value.split("::double=")[-1]
        numerical_part = numerical_part[:len(numerical_part)-3]
        # Convert the numerical part to a float and append to the list
        altitude = float(numerical_part)
    print(latitude,longitude,altitude)
    s = blfliter(latitude,longitude,altitude)
    data = str(latitude)+","+str(longitude)+","+ str(altitude)+","+ str(s)+"\n"
    transfer(data)
    time.sleep(5)
    id = id+1


# In[196]:


import os
try:
    os.remove("example.txt")
    print(f"File '{example.txt}' deleted successfully.")
except FileNotFoundError:
    print(f"File '{example.txt}' not found.")
except Exception as e:
    print(f"An error occurred: {e}")


# In[ ]:




