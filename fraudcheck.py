import json
from datetime import datetime
from geopy.distance import geodesic
from confluent_kafka import Consumer, KafkaError, Producer
from dateutil import parser

consumer_conf = {
    'bootstrap.servers': '####',
    'group.id': 'new-fraudetection',
    'auto.offset.reset': 'earliest',
    'sasl.mechanisms': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'sasl.username': '####',
    'sasl.password': '####'
}

consumer = Consumer(consumer_conf) 
#producer = Producer({'bootstrap.servers': 'pkc-921jm.us-east-2.aws.confluent.cloud:9092'})
consumer.subscribe(['transaction_data', 'location_data'])

producer_conf = {
    'bootstrap.servers': '####',
    'sasl.mechanisms': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'sasl.username': '####',
    'sasl.password': '####'
}
producer = Producer(**producer_conf)
device_locations = {}

def parse_timestamp(timestamp_str):
    try:
        return parser.parse(timestamp_str)
    except ValueError as e:
        print(f"Error parsing timestamp: {timestamp_str} - {str(e)}")
        return None

def calculate_speed(distance, time_difference):
    if time_difference > 0:  
        return distance / time_difference  
    return 0

def check_fraud(transaction, location):
    trans_loc = (transaction['Location Latitude'], transaction['Location Longitude'])
    loc_loc = (location['Latitude'], location['Longitude'])
    distance = geodesic(trans_loc, loc_loc).meters
    
    trans_time = parse_timestamp(transaction['Timestamp'])
    loc_time = parse_timestamp(location['Time'])

    if trans_time is None or loc_time is None:
        print("Invalid timestamps provided; cannot evaluate fraud.")
        return

    time_difference = abs((loc_time - trans_time).total_seconds())
    calculated_speed = calculate_speed(distance, time_difference)
    reported_speed = float(location.get('Speed', 0))

    if calculated_speed > (reported_speed + 1):
        print(f"Potential Fraud Detected for Transaction ID: {transaction['Transaction ID']}")
        # Send to fraud_transactions topic
        producer.produce('fraud_transactions', json.dumps(transaction).encode('utf-8'))
        producer.flush()
    else:
        print(f"No Fraud Detected for Transaction ID: {transaction['Transaction ID']}")

    print_details(transaction, loc_time, trans_time, time_difference/60, trans_loc, loc_loc, distance, location, calculated_speed, reported_speed)

def print_details(transaction, loc_time, trans_time, time_difference, trans_loc, loc_loc, distance, location, calculated_speed, reported_speed):
    print(f"Transaction Details: User ID: {transaction['User ID']}, Card Number: {transaction['Card Number']}, Amount: {transaction['Amount']}")
    print(f"Transaction Time: {trans_time}, Location Time: {loc_time}, Time Difference: {time_difference} minutes")
    print(f"Transaction Location: {trans_loc}, Device Location: {loc_loc}, Distance: {distance} meters")
    print(f"Reported Speed at Location: {reported_speed}, Calculated Speed: {calculated_speed}")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(msg.error())
                break

        data = json.loads(msg.value().decode('utf-8'))

        if msg.topic() == 'location_data':
            device_id = data.get('DeviceId')
            if device_id and all(key in data for key in ['Latitude', 'Longitude', 'Time', 'Speed']):
                device_locations[device_id] = data
            else:
                print("'DeviceId' not found in the location data message")

        elif msg.topic() == '####':
            device_id = data.get('Device ID')
            if device_id:
                if device_id in device_locations:
                    check_fraud(data, device_locations[device_id])
                else:
                    print(f"Device ID {device_id} not found in location data.")
            else:
                print("Key 'Device ID' not found in the transaction data message:", data)

finally:
    consumer.close()