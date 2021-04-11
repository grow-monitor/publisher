import os
import random
import time

import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from grow.moisture import Moisture


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


if __name__ == "__main__":
    load_dotenv()
    publisher = Publisher(
        os.getenv("USERNAME"),
        os.getenv("PASSWORD"),
        os.getenv("HOST"),
        int(os.getenv("PORT")),
    )

    while True:
        publisher.publish("mock/moisture", random.random())
        publisher.publish("mock/saturation", random.uniform(50, 900))
        time.sleep(5)
