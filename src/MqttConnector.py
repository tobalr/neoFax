import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
class MqttConnector:
    'Responsible for mqtt pub/sub'
    client = None
    onMessageReceived = None
    topics = []


    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        for topic in self.topics:
            print(topic)
            self.client.subscribe(topic)

    # The callback for when a PUBLISH message is received from the server.


    def on_message(self, client, userdata, msg):
        print(msg.topic+" "+str(msg.payload))
        self.onMessageReceived(msg.topic, msg.payload)

    def updateSubscriptions(self, topics):
        self.topics = topics
        self.client.reconnect()


    def __init__(self, onMessageReceived):
        self.onMessageReceived = onMessageReceived
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.connect()

        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        self.client.loop_start()

    def connect(self):
        self.client.connect("iot.eclipse.org", 1883, 60)


    def publish(self, channel, message):
        publish.single(channel, message, hostname="iot.eclipse.org")