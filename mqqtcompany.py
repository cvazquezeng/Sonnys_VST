import paho.mqtt.client as mqtt
import pandas as pd
import os

# Define the MQTT broker URL and port
broker_url = "us2.mqtt.sageclarity.com"
broker_port = 443

# Define the WebSocket path
broker_ws_path = "/mqtt"

# Define the MQTT client ID (can be any unique identifier)
client_id = "1718753522698"

# Define the username and password
username = "RZ7DjPGb"
password = "gBHFR7en"

# Define the specific topic to subscribe to
specific_topic = "HOST/Andon/71/+"

# Define the MQTT client
client = mqtt.Client(client_id, transport="websockets", protocol=mqtt.MQTTv311)

# Set the WebSocket path
client.ws_set_options(path=broker_ws_path)

# Set the username and password
client.username_pw_set(username, password)

# Define the CSV file path
csv_file = 'mqtt_data_subs77.csv'

# Create a new CSV file with headers if it doesn't exist
if not os.path.exists(csv_file):
    df = pd.DataFrame(columns=['Topic', 'Payload'])
    df.to_csv(csv_file, index=False)

# Define the callback functions for connection and message
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    if rc == 0:
        client.subscribe(specific_topic)
        print(f"Subscribed to topic: {specific_topic}")
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode('utf-8')
    except UnicodeDecodeError:
        payload = msg.payload.hex()

    # Use a temporary DataFrame to handle the new data
    new_data = pd.DataFrame([[msg.topic, payload]], columns=['Topic', 'Payload'])
    
    # Append new data to the CSV file
    new_data.to_csv(csv_file, mode='a', header=False, index=False)
    
    print(f"Message received from topic {msg.topic}: {payload}")

# Assign the callback functions to the MQTT client
client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT broker
client.tls_set()  # This enables SSL/TLS
client.connect(broker_url, broker_port)

# Start the MQTT client loop
client.loop_start()

# Keep the script running
try:
    while True:
        pass
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()
