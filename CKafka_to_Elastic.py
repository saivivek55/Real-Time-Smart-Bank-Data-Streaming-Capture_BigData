from confluent_kafka import Consumer, KafkaException
from elasticsearch import Elasticsearch
import json

client = Elasticsearch(
  "https:abc",
  api_key="NA"
)

kafka_config = {
    'bootstrap.servers': '####',  
    'group.id': 'fraud_card',
    'security.protocol': 'SASL_SSL',  
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': '###',  
    'sasl.password': '####'  
}

# Create Kafka consumer
consumer = Consumer(kafka_config)
consumer.subscribe(['abc'])  

def index_document(doc):
    try:
        res = client.index(index="abc", body=doc)  
        print(res)
    except Exception as e:
        print("Failed to index document: ", e)


try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaException._PARTITION_EOF:
                continue
            else:
                print(msg.error())
                break

        print('Received message: {}'.format(msg.value().decode('utf-8')))
        document = json.loads(msg.value().decode('utf-8'))  
        index_document(document)

except KeyboardInterrupt:
    pass
finally:
    consumer.close()
