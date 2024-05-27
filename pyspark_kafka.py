#!/usr/bin/env python
# coding: utf-8

# In[2]:


# Create the Spark Session
from pyspark.sql import SparkSession

spark = (
    SparkSession 
    .builder 
    .appName("Kafka Spark Streaming") 
    .config("spark.streaming.stopGracefullyOnShutdown", True) 
    .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0')
    .config("spark.sql.shuffle.partitions", 8)
    .master("local[*]") 
    .getOrCreate()
)

spark


# In[3]:


kafka_df = (
    spark
    .readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "ed-kafka:29092")
    .option("subscribe", "t-data")
    .option("startingOffsets", "earliest")
    .load()
)


# In[4]:


# View schema for raw kafka_df
kafka_df.printSchema()
#kafka_df.show()
#kafka_df.rdd.getNumPartitions()


# In[5]:


from pyspark.sql.functions import expr

kafka_json_df = kafka_df.withColumn("value", expr("cast(value as string)"))
kafka_json_df


# In[6]:


# Schema of the Pyaload

from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType
json_schema = StructType([
    StructField("Transaction ID", StringType(), nullable=False),
    StructField("User ID", StringType(), nullable=False),
    StructField("Name", StringType(), nullable=False),
    StructField("Timestamp", DoubleType(), nullable=False),
    StructField("Amount", DoubleType(), nullable=False),
    StructField("Card Number", StringType(), nullable=False),
    StructField("Merchant ID", StringType(), nullable=False),
    StructField("Merchant", StringType(), nullable=False),
    StructField("Merchant_category", StringType(), nullable=False),
    StructField("Location Latitude", StringType(), nullable=False),
    StructField("Location Longitude", StringType(), nullable=False),
    StructField("Transaction Type", StringType(), nullable=False),
    StructField("Transaction_device", StringType(), nullable=False)
])


# In[7]:


from pyspark.sql.functions import from_json,col

streaming_df = kafka_json_df.withColumn("values_json", from_json(col("value"), json_schema)).selectExpr("values_json.*")


# In[8]:


# To the schema of the data, place a sample json file and change readStream to read 
streaming_df.printSchema()


# In[11]:


import shutil
import os

def delete_folder(folder_path):
    # Check if the folder exists
    if os.path.exists(folder_path):
        # Iterate over all files and subdirectories in the folder
        for root, dirs, files in os.walk(folder_path, topdown=False):
            # Remove all files
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)
            # Remove all subdirectories
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                os.rmdir(dir_path)
        # Remove the top-level folder itself
        os.rmdir(folder_path)
        print(f"All files and folders in '{folder_path}' have been deleted.")
    else:
        print(f"Folder '{folder_path}' does not exist.")

# Call the function with the path to the folder you want to delete
delete_folder("output")


# In[12]:


(streaming_df
 .writeStream
 .format("csv")
 .outputMode("append")
 .option("path","output/")
 .option("checkpointLocation", "checkpoint_dir_kafka_1")
 .start()
 .awaitTermination())


# In[ ]:




