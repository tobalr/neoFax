from Crypto.PublicKey import RSA
from MqttConnector import MqttConnector
from time import sleep
import uuid
import gen.messages_pb2 as pb_msg

def generateKeyPair(): 
    key = RSA.generate(2048)
    private_key = key.export_key()
    # file_out = open("private.pem", "wb")
    # file_out.write(private_key)

    public_key = key.publickey().export_key()
    # file_out = open("receiver.pem", "wb")
    # file_out.write(public_key)
    return (public_key, private_key)

def onMessageReceived(topic, message):
    print("Msg receieved:\n>" + str(message) + "on topic:\n>" + str(topic))
    pairRequest = pb_msg.PairRequest()
    pairRequest.ParseFromString(message)
    clientChannel = pairRequest.receiving_topic
    subscribeForIncomming(clientChannel)
    pubKeyClient = pairRequest.pubKey
    
    print("received pub key:" + pubKeyClient)

    faxChannel = getChannelId()

    pairConfirm = pb_msg.PairConfirm()
    pairConfirm.receiving_topic = faxChannel
    serializedMessage = pairConfirm.SerializeToString()

    publishPairingConfirm(clientChannel, serializedMessage)


def publishPairingConfirm(clientChannel, message):
    mqttConnector.publish(clientChannel, message)


def subscribeForIncomming(clientChannel):
    knownClientTopics.append(clientChannel)
    updateSubscriptions()


def getChannelId():
    return str(uuid.uuid4())

def updateSubscriptions():
    mqttConnector.updateSubscriptions(pairingTopics + knownClientTopics)

def openForPairing():
    pairingId = getChannelId()
    pairingTopics.append(pairingId)
    updateSubscriptions()
    printPairingQR(pairingId)

def printPairingQR(pairingId):
    print("Now listening for new paring on: "+pairingId)

knownClientTopics = []
pairingTopics = []
keyPair = generateKeyPair()
print(keyPair)


mqttConnector = MqttConnector(onMessageReceived)
sleep(2)

openForPairing()
sleep(120)