# -*- coding: UTF-8 -*-

import paho.mqtt.client as mqtt
import subprocess
import time
import configparser
import socket

serverName = ""

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	print("Connected to MQTT broker with result code " + str(rc))

# Connect to MQTT broker
def connect(client):
	print("Connecting to " + serverName)
	client.connect(serverName, 1883, 60)

# Start
print("inputRaspiPiTemp starting...")

host = socket.gethostname()

# Read configuration
config = configparser.ConfigParser()
config.read("homecontrol.ini")
serverName = config.get("settings", "server")

# Connect to MQTT
client = mqtt.Client()
client.on_connect = on_connect

connect(client)
client.loop_start()

while True:
	result = subprocess.check_output(["/opt/vc/bin/vcgencmd", "measure_temp"])
	result = result.decode()
	result = result[5:]
	result = result[:-3]
	print(result)
	client.publish("homecontrol/rawInput/RaspiPiTemp/" + host, result)
	time.sleep(5 * 60)


