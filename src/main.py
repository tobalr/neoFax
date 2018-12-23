from Crypto.PublicKey import RSA
from MqttConnector import MqttConnector
from time import sleep
import uuid

def generateKeyPair():
    key = RSA.generate(2048)
    private_key = key.export_key()
    # file_out = open("private.pem", "wb")
    # file_out.write(private_key)

    public_key = key.publickey().export_key()
    # file_out = open("receiver.pem", "wb")
    # file_out.write(public_key)
    return (public_key, private_key)

pairingTopics = []
keyPair = generateKeyPair()
print(keyPair)

mqttConnector = MqttConnector()
sleep(2)

def openForPairing():
    pairingId = str(uuid.uuid4())
    pairingTopics.append(pairingId)
    mqttConnector.updateSubscriptions(pairingTopics)
    printPairingQR(pairingId)

def printPairingQR(pairingId):
    print("Now listening for new paring on: "+pairingId)

openForPairing()
sleep(10)