import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

import CommunicationHelper

KEEPALIVE_SECONDS = 60

PORT = 1883

# HOST = "iot.eclipse.org"
HOST = "0.0.0.0"


class MqttConnector:
    """Responsible for mqtt pub/sub"""
    client = None
    onMessageReceived = None
    topics = []

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self.subscribeToAllTopics()

    def subscribeToAllTopics(self):
        print("Now listening on: ")
        for topic in self.topics:
            fullTopic = topic + "/#"
            print("   " + fullTopic)
            self.client.subscribe(fullTopic)

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        topicParts = msg.topic.partition("/")
        print("Message received on topic: ")
        print(topicParts)
        msgType = CommunicationHelper.getMsgType(topicParts[2])
        self.onMessageReceived(topicParts[0], msgType, msg.payload)

    def __init__(self, onMessageReceived):
        self.onMessageReceived = onMessageReceived
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.connect()
        self.client.loop_start()

    def updateSubscriptions(self, topics):
        self.topics = topics
        self.subscribeToAllTopics()

    def connect(self):
        self.client.connect(HOST, PORT, KEEPALIVE_SECONDS)

    def publish(self, channel, message, messageType):
        topicPostfix = CommunicationHelper.getMsgStringType(messageType)
        fullChannel = channel + "/" + topicPostfix
        print("Publish to channel: " + fullChannel + " Msg:\n" + str(message))
        publish.single(fullChannel, message, hostname=HOST, qos=2)
