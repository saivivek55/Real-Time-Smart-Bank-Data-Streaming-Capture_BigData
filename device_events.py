# Generate random events data
import datetime
import time
import uuid
import random
import json
from faker import Faker

fake = Faker()


# Initialize counters for every tenth transaction logic
common_device_id = "d39d92c3-28ac-4755-9abf-a48f390347d2"
common_name = "John Wick"
common_user_id = "DEAD975D"
john_wick_cards = ["4124731290123316", "62358672243501927", "4128473847394747"]
coomon_device = "mobile"
counter = 1  # Start from 1 for ease of modulo operation


# Generate event data from devices
def generate_events(offset=0):
    i= random.randint(1, 10)
    if i%3==0:
         return {
            "Transaction ID": fake.uuid4(),
            "User ID": fake.uuid4(),
            "Name": fake.name(),
            "Timestamp": datetime.datetime.now().timestamp(),
            "Amount": round(random.uniform(5.0, 1000.0), 2),
            "Card Number": ''.join([str(random.randint(0, 9)) for _ in range(16)]),
            "Merchant ID": str(random.randint(10000000, 999999999)),
            "Merchant": fake.company(),
            "Merchant_category": fake.random_element(elements=('Retail', 'Restaurant', 'Travel', 'Online', 'Entertainment')),
            "Location Latitude": random.uniform(-90, 90),
            "Location Longitude": random.uniform(-180, 180),
            "Transaction Type": random.choice(['online']),
            "Transaction_device": random.choice(['mobile', 'tablet'])
        }
    else:
        return {
            "Transaction ID": fake.uuid4(),
            "User ID": '101',
            "Name": "Prayag",
            "Timestamp": datetime.datetime.now().timestamp(),
            "Amount": round(random.uniform(5.0, 1000.0), 2),
            "Card Number": ''.join([str(random.randint(0, 9)) for _ in range(16)]),
            "Merchant ID": str(random.randint(10000000, 999999999)),
            "Merchant": fake.company(),
            "Merchant_category": fake.random_element(elements=('Retail', 'Restaurant', 'Travel', 'Online', 'Entertainment')),
            "Location Latitude": 37.3359139,
            "Location Longitude": -121.8952841,
            "Transaction Type": random.choice(['online']),
            "Transaction_device": random.choice(['mobile', 'tablet'])
        }



if __name__ == "__main__":
    _offset = 10000
    while True:
        print(generate_events(offset=_offset))
        time.sleep(random.randint(0, 5))
        _offset += 1
