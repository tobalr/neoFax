from CommunicationHelper import generateKeyPair, getMsgType, MsgType, getChannelId
from Connection import Connection
from MqttConnector import MqttConnector
import gen.messages_pb2 as pb_msg


class CommunicationManager:


    def __init__(self):
        self.keyPair = self.getKeyPair()
        self.mqttConnector = MqttConnector(self.onMessageReceived)
        self.connections = {}
        self.pairingChannels = []

    def getKeyPair(self):
        return generateKeyPair()

    def getPairingTopics(self):
        return self.pairingChannels

    def getCommunicationChannels(self):
        rxChannels = []
        for connection in self.connections:
            rxChannels.append(connection.rxChannel)
        return rxChannels

    def getAllChannels(self):
        return self.getPairingTopics() + self.getCommunicationChannels()

    def onMessageReceived(self, channel, msgType, message):
        if msgType == MsgType.PairRequest:
            self.onPairRequestReceieved(message)
        elif msgType == MsgType.PairConfirm:
            self.onReceivePairConfirmation(channel, message)

    def onReceivePairConfirmation(self, channel, message):
        print("Received a pairing confirmation")
        pairConfirm = pb_msg.PairConfirm()
        pairConfirm.ParseFromString(message)
        txChannel = pairConfirm.receiving_topic
        rxChannel = channel
        self.addConnection(rxChannel, txChannel,
                           None)  # ToDo missing pubkey - must be receieved during pair

    def onPairRequestReceieved(self, message):
        print("Received a pair request")
        pairRequest = pb_msg.PairRequest()
        pairRequest.ParseFromString(message)
        txChannel = pairRequest.receiving_topic
        rxChannel = getChannelId()
        self.addConnection(rxChannel, txChannel, pairRequest.pubKey)
        pairConfirm = pb_msg.PairConfirm()
        pairConfirm.receiving_topic = rxChannel
        serializedMessage = pairConfirm.SerializeToString()
        self.mqttConnector.publish(txChannel, serializedMessage, MsgType.PairConfirm)

    def openForPairRequests(self):
        print("Open for pair requests")
        pairChannelId = getChannelId()
        self.subscribeToPairingChannel(pairChannelId)
        return pairChannelId

    def pair(self, pairId):
        print("Pairing with: " + pairId)
        rxChannel = getChannelId()
        self.subscribeToPairingChannel(rxChannel)
        pairRequest = pb_msg.PairRequest()
        pairRequest.receiving_topic = rxChannel
        pairRequest.pubKey = self.keyPair[0]
        pairRequestMessage = pairRequest.SerializeToString()
        self.mqttConnector.publish(pairId, pairRequestMessage, MsgType.PairRequest)

    def subscribeToPairingChannel(self, pairingChannel):
        print("Subscribing to pairing channel=" + pairingChannel)
        self.pairingChannels.append(pairingChannel)
        self.updateSubscriptions()

    def updateSubscriptions(self):
        self.mqttConnector.updateSubscriptions(self.getAllChannels())

    def addConnection(self, rxChannel, txChannel, pubKeyClient):
        connection = Connection(rxChannel, txChannel, pubKeyClient)
        self.connections[rxChannel] = connection
        print("A new connection has been added. \n"
              "RxChannel=" + connection.rxChannel + "\n"
              "TxChannel=" + connection.txChannel + "\n"
              "TxPubKey=" + connection.pubKey)
