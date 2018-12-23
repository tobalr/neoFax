import sys
import paho.mqtt.publish as publish
from Crypto.PublicKey import RSA
import uuid
from MqttConnector import MqttConnector
import gen.messages_pb2 as pb_msg

pairPath=""
pairIdFax = sys.argv[1]

def generateKeyPair():
    key = RSA.generate(2048)
    private_key = key.export_key()
    # file_out = open("private.pem", "wb")
    # file_out.write(private_key)

    public_key = key.publickey().export_key()
    # file_out = open("receiver.pem", "wb")
    # file_out.write(public_key)
    return (public_key, private_key)

def onMessageRecieved(topic, message):
    print(topic)
    print(message)




keyPair = generateKeyPair()
pairIdClient = str(uuid.uuid4())

mqttConnector = MqttConnector(onMessageRecieved)
mqttConnector.updateSubscriptions([pairIdClient])

pairRequest = pb_msg.PairRequest()
pairRequest.receiving_topic = pairIdFax
pairRequest.pubKey = keyPair[0]
pairRequestMsg = pairRequest.SerializeToString()
print(pairRequestMsg)
mqttConnector.publish(pairIdFax, pairRequestMsg)

while True:
    pass