import json
import os
import pathlib
import random
import sys
import time
from datetime import datetime

import paho.mqtt.client as mqtt
import yaml
from dotenv import load_dotenv
from grow.moisture import Moisture

from config import HOST, PASSWORD, PORT, SETTINGS_FILE, USERNAME


class Config(object):
    """
    Partial implementation of Config class from 
    https://github.com/pimoroni/grow-python/blob/master/examples/monitor.py
    """

    def __init__(self, id):
        with open(pathlib.Path(SETTINGS_FILE)) as config_file:
            _config = yaml.safe_load(config_file)
        self.config = _config.get("channel{}".format(id))

    @property
    def wet_point(self):
        return self.config.get("wet_point")

    @property
    def dry_point(self):
        return self.config.get("dry_point")


class Sensor(object):
    """
    Light wrapper on top of grow.Moisture
    """

    def __init__(self, channel, wet_point=None, dry_point=None):
        self._sensor = Moisture(channel, wet_point=wet_point, dry_point=dry_point)
        self.topic = "grow/soil/{}".format(channel)

    @property
    def is_valid(self):
        return self._sensor.active

    @property
    def has_new_data(self):
        return self._sensor.new_data

    @property
    def moisture(self):
        return self._sensor.moisture

    @property
    def saturation(self):
        return self._sensor.saturation


class Publisher(object):
    def __init__(self, username, password, host, port):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
        self.client.username_pw_set(username, password)
        self.client.connect(host, port)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected successfully")
        else:
            print("Connect returned result code: {}".format(rc))

    def on_publish(self, client, userdata, mid):
        print("Published message_id={}".format(mid))

    def publish(self, topic, payload):
        return_code, message_id = self.client.publish(topic, payload, qos=2)
        return return_code, message_id


def main():
    channel = int(sys.argv[1])
    cfg = Config(channel)
    sensor = Sensor(channel, wet_point=cfg.wet_point, dry_point=cfg.dry_point)
    publisher = Publisher(USERNAME, PASSWORD, HOST, PORT)

    while True:
        if not (sensor.is_valid and sensor.has_new_data):
            continue
        timestamp = datetime.now().astimezone().isoformat()
        moisture = {"timestamp": timestamp, "value": sensor.moisture}
        saturation = {"timestamp": timestamp, "value": sensor.saturation}
        publisher.publish(sensor.topic + "/moisture", json.dumps(moisture))
        publisher.publish(sensor.topic + "/saturation", json.dumps(saturation))


if __name__ == "__main__":
    main()
