import sys
from time import sleep
from Crypto.PublicKey import RSA
import uuid
from MqttConnector import MqttConnector
import gen.messages_pb2 as pb_msg

pairPath = ""
pairIdFax = sys.argv[1]


def generateKeyPair():
    key = RSA.generate(2048)
    private_key = key.export_key()
    # file_out = open("private.pem", "wb")
    # file_out.write(private_key)

    public_key = key.publickey().export_key()
    # file_out = open("receiver.pem", "wb")
    # file_out.write(public_key)
    return public_key, private_key


def onMessageRecieved(topic, message):
    print("Msg received:\n>" + str(message) + "\non topic:\n>" + str(topic))


keyPair = generateKeyPair()
pairIdClient = str(uuid.uuid4())

mqttConnector = MqttConnector(onMessageRecieved)
mqttConnector.updateSubscriptions([pairIdClient])
sleep(2)

pairRequest = pb_msg.PairRequest()
pairRequest.receiving_topic = pairIdClient
pairRequest.pubKey = keyPair[0]
pairRequestMsg = pairRequest.SerializeToString()
print("Listening for pair response on: " + str(pairRequestMsg))
mqttConnector.publish(pairIdFax, pairRequestMsg)

while True:
    sleep(10)
