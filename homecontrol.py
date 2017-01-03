# -*- coding: UTF-8 -*-

import datetime
import paho.mqtt.client as mqtt
import sqlite3
import configparser

serverName = ""
dbName = ""
rawMQTTTopic = "homecontrol/rawInput/#"
structuredMQTTTopic = "homecontrol/structuredInput/#"
systemMQTTTopic = "$SYS/#"

def log(message):
    message = str(datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")) + ": " + str(message)
    print(message)
    
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    log("Connected with MQTT broker with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
#    client.subscribe(systemMQTTTopic)
    log("Subscribing to " + rawMQTTTopic)
    client.subscribe(rawMQTTTopic)
    log("Subscribing to " + structuredMQTTTopic)
    client.subscribe(structuredMQTTTopic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    log(msg.topic + ": " + msg.payload.decode())
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("INSERT INTO rawInput VALUES (" + str(int(datetime.datetime.now(datetime.timezone.utc).timestamp())) + ", '" + msg.topic + "', '" + msg.payload.decode() + "', 0)")
    conn.commit()
    conn.close()

# Start
log("HomeControl starting...")

# Read configuration
config = configparser.ConfigParser()
config.read("homecontrol.ini")
serverName = config.get("settings", "server")
dbName = config.get("settings", "db")

# Check DB
conn = sqlite3.connect(dbName)
c = conn.cursor()
c.execute("create table if not exists rawInput (timestamp INTEGER, topic TEXT, message TEXT, handled INTEGER)")
conn.commit()
conn.close()

log("Connecting to MQTT server " + serverName)
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(serverName, 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()

