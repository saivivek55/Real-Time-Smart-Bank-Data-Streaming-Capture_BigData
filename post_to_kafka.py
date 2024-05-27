from kafka import KafkaProducer, KafkaConsumer
import time
import random
from device_events import generate_events
import uuid

__bootstrap_server = "ed-kafka:29092"


def post_to_kafka(data):
    print('data: '+ str(data))
    producer = KafkaProducer(bootstrap_servers=__bootstrap_server)
    producer.send('t-data', key=bytes(str(uuid.uuid4()), 'utf-8'), value=data)
    #producer.flush()
    producer.close()
    print("Posted to topic")


if __name__ == "__main__":
    _offset = 10000
    while True:
        post_to_kafka(bytes(str(generate_events(offset=_offset)), 'utf-8'))
        time.sleep(random.randint(0, 5))
        _offset += 1