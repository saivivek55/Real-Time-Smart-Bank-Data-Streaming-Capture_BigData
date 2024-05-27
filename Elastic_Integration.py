#!/usr/bin/env python
# coding: utf-8

# In[1]:


from elasticsearch import Elasticsearch
import time
from datetime import datetime


# In[2]:


# Found in the 'Manage this deployment' page
CLOUD_ID = "xxx"


# In[3]:


# Found in the 'Management' page under the section 'Security'
API_KEY = "xxx"
#MGlmbTU0NEJ4Zk8wVTEzSUVwWUQ6NUtwZlNXc0NRbTJhaXp4Vmw4LWhtZw==
#https://c548d90314b149f993fa985c277fc9d1.us-central1.gcp.cloud.es.io:443
#https://c548d90314b149f993fa985c277fc9d1.us-central1.gcp.cloud.es.io:443


# In[4]:


# Create the client instance
client = Elasticsearch(
    cloud_id=CLOUD_ID,
    api_key=API_KEY,
)
          


# In[5]:


client.info()


# In[6]:


def create_document(data):
    event_id = datetime.timestamp(datetime.now())
    Transcation = {
        "Latitude": data[0],
        "Longitude": data[1],
        "Altitude": data[2],
        "Type": data[3],
        "_extract_binary_content": "true",
        "_reduce_whitespace": "true",
        "_run_ml_inference": "true"
        }
    doc.append({"index": {"_index": "iotdata", "_id": event_id}})
    doc.append(Transcation)
    #print(doc)
    #print()
    return doc
    


# In[7]:


doc=[]


# In[8]:


def read_file_line_by_line(file_name):
    try:
        with open(file_name, 'r') as file:
            for line in file:
                s = line.strip()
                #print(s)
                data = s.split(',')
                #print(data)
                data_float = [float(num) for num in data]
                #print(data_float)
                create_document(data)# .strip() removes leading/trailing whitespace and newline characters
    except FileNotFoundError:
        print(f"File '{file_name}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
file_name = "example.txt"
read_file_line_by_line(file_name)


# In[9]:


doc


# In[10]:


client.bulk(operations=doc, pipeline="ent-search-generic-ingestion")


# In[ ]:




