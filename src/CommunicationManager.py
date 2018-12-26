from CommunicationHelper import generateKeyPair, getCommType, CommType, getChannelId
from MqttConnector import MqttConnector
import gen.messages_pb2 as pb_msg


class CommunicationManager:
    keypair = None
    mqttConnector = None
    knownClientFaxChannels = []
    pairingTopics = []

    def __init__(self):
        self.keypair = self.getKeyPair()
        self.mqttConnector = MqttConnector(self.onMessageReceived)

    def getKeyPair(self):
        return generateKeyPair()

    def getPairingTopics(self):
        return self.pairingTopics

    def getKnownClientTopics(self):
        return self.knownClientFaxChannels

    def getAllTopics(self):
        return self.getPairingTopics() + self.getKnownClientTopics()

    def onMessageReceived(self, topic, message):
        print("Msg received:\n>" + str(message) + "\non topic:\n>" + str(topic))

        messageType = getCommType(topic)
        if messageType == CommType.PairRequest:
            print("Received a pair request")
            pairRequest = pb_msg.PairRequest()
            pairRequest.ParseFromString(message)
            clientChannel = pairRequest.receiving_topic
            faxChannel = getChannelId()
            self.addNewClient(clientChannel, faxChannel)

            pubKeyClient = pairRequest.pubKey
            print("received pub key:" + pubKeyClient)

            pairConfirm = pb_msg.PairConfirm()
            pairConfirm.receiving_topic = faxChannel
            serializedMessage = pairConfirm.SerializeToString()
            self.publishPairingConfirm(clientChannel, serializedMessage)

    def openNewPairing(self):
        pairingId = getChannelId()
        self.addNewParingTopic(pairingId)
        return pairingId

    def addNewParingTopic(self, pairingId):
        self.pairingTopics.append(pairingId)
        self.updateSubscriptions()

    def addNewClient(self, clientChannel, faxChannel):
        self.knownClientFaxChannels.append(faxChannel)
        self.updateSubscriptions()
        print("A new client has been added. \nMessages receiving on "+faxChannel+" and sending on "+clientChannel)

    def updateSubscriptions(self):
        self.mqttConnector.updateSubscriptions(self.getAllTopics())

    def publishPairingConfirm(self, clientChannel, message):
        self.mqttConnector.publish(clientChannel, message)
