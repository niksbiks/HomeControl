# -*- coding: UTF-8 -*-

import datetime
import paho.mqtt.client as mqtt
import sqlite3
import configparser
import logging
import os
from bottle import get, run, debug

serverName = ""
dbName = ""
log = ""
loglevel = ""
rawMQTTTopic = "homecontrol/rawInput/#"
structuredMQTTTopic = "homecontrol/structuredInput/#"
systemMQTTTopic = "$SYS/#"

def log(message):
    msg = str(datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")) + ": " + str(message)
    print(msg)
    

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
#logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filename=log, level=logging.DEBUG)
#logging.debug('This message should appear on the console')
#logging.info('So should this')
#logging.warning('And this, too')

# Check if this is the working child process for Bottle
if os.environ.get('BOTTLE_CHILD'):
	log("HomeControl worker process starting...")

	# Read configuration
	config = configparser.ConfigParser()
	config.read("homecontrol.ini")
	serverName = config.get("settings", "server")
	dbName = config.get("settings", "db")
	logname = config.get("settings", "log")
	loglevel = config.get("settings", "loglevel")

	# Check DB
	conn = sqlite3.connect(dbName)
	c = conn.cursor()
	c.execute("CREATE TABLE IF NOT EXISTS rawInput (timestamp INTEGER, topic TEXT, message TEXT, handled INTEGER)")
	c.execute("CREATE TABLE IF NOT EXISTS measurements (timestamp INTEGER, topic TEXT, value TEXT, derived INTEGER, type TEXT, unit TEXT, valueType TEXT)")
	c.execute("CREATE TABLE IF NOT EXISTS units (name TEXT)")
	c.execute("INSERT INTO units VALUES ('oC')")
	c.execute("INSERT INTO units VALUES ('kWh')")
	c.execute("CREATE TABLE IF NOT EXISTS valueTypes (name TEXT)")
	c.execute("INSERT INTO valueTypes VALUES ('Value')")
	c.execute("INSERT INTO valueTypes VALUES ('Accumulated')")
	c.execute("INSERT INTO valueTypes VALUES ('Event')")
	c.execute("CREATE TABLE IF NOT EXISTS types (name TEXT)")
	c.execute("INSERT INTO types VALUES ('Temperature')")
	c.execute("INSERT INTO types VALUES ('TemperatureSeries')")
	c.execute("INSERT INTO types VALUES ('RainSeries')")
	c.execute("INSERT INTO types VALUES ('Activated')")
	conn.commit()
	conn.close()

	log("Connecting to MQTT server " + serverName)
	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_message = on_message

	client.connect(serverName, 1883, 60)

	client.loop_start()
else:
	log("HomeControl master process starting...")

@get('/hello/<name>')
def index(name):
	result = {"x":"y", "z":name}
	return result

@get('/static/<filepath:path>')
def server_static(filepath):
	return static_file(filepath, root='/path/to/your/static/files')
        
debug(True)
run(host='localhost', port=8080, reloader=True)
