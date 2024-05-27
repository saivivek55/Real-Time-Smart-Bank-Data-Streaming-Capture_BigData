import json
from faker import Faker
import random
import time
from confluent_kafka import Producer
from datetime import datetime, timedelta

fake = Faker()

def create_producer():
    config= {
        'bootstrap.servers': '####',
        'client.id': 'transaction_data',
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'PLAIN',
        'sasl.username': '####',
        'sasl.password': '####'
    }
    return Producer(config)


producer = create_producer()
topic = 'transaction_data'

# Configuration for John Wick's transactions
common_device_id = "####"
common_name = "John Wick"
common_user_id = "DEAD975D"
john_wick_cards = ["4124731290123316", "62358672243501927", "4128473847394747"]
common_device = "mobile"
counter = 1  

def generate_record(counter):
    # Generating a timestamp that is 7 hours behind UTC, within the last 2 minutes
    timestamp = datetime.utcnow() - timedelta(hours=7, minutes=random.randint(0, 2))
    
    if counter % 10 == 0:
        # Specific configuration for John Wick
        device_id, name, user_id, card_number, t_device = common_device_id, common_name, common_user_id, random.choice(john_wick_cards), common_device
        latitude, longitude = str(fake.coordinate(center=37.3359139, radius=0.001)), str(fake.coordinate(center=-121.8952841, radius=0.001))
    else:
        # for others
        device_id, name, user_id = fake.uuid4(), fake.name(), ''.join(random.choices('0123456789ABCDEF', k=8))
        card_number, t_device = ''.join(random.choices('0123456789', k=16)), fake.random_element(['mobile', 'tablet'])
        latitude, longitude = str(fake.coordinate(center=37.3382, radius=0.1)), str(fake.coordinate(center=-121.8863, radius=0.1))

    return {
        "Transaction ID": fake.uuid4(),
        "User ID": user_id,
        "Device ID": device_id,
        "Name": name,
        "Timestamp": timestamp.isoformat(),
        "Amount": round(random.uniform(5.0, 1000.0), 2),
        "Card Number": card_number,
        "Merchant ID": str(random.randint(10000000, 999999999)),
        "Merchant": fake.company(),
        "Merchant_category": fake.random_element(elements=('Retail', 'Restaurant', 'Travel', 'Online', 'Entertainment')),
        "Location Latitude": latitude,
        "Location Longitude": longitude,
        "Transaction Type": random.choice(['online']),
        "Transaction_device": t_device
    }


def delivery_report(err, msg):
    if err:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()}')

try:
    while True:
        data = generate_record(counter)
        json_data = json.dumps(data)
        producer.produce(topic, json_data, callback=delivery_report)
        producer.poll(0)  
        print("Produced:", json_data)
        time.sleep(5)  
        counter += 1
except KeyboardInterrupt:
    print("\nStopping the producer.")
finally:
    producer.flush()  