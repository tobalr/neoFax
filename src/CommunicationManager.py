import EncryptionHelper
from CommunicationHelper import generateKeyPair, getMsgType, MsgType, getChannelId
from Connection import Connection
from MqttConnector import MqttConnector
import gen.messages_pb2 as pb_msg


class CommunicationManager:

    def __init__(self, onPrintMessageReceivedCallback):
        self.printMessageCallback = onPrintMessageReceivedCallback
        self.keyPair = self.getKeyPair()
        self.mqttConnector = MqttConnector(self.onMessageReceived)
        self.connections = {}
        self.pairingChannels = []
        self.tempConnection = None

    def getKeyPair(self):
        return generateKeyPair()

    def getPairingChannels(self):
        return self.pairingChannels

    def getCommunicationChannels(self):
        rxChannels = []
        for rxChannel in self.connections.keys():
            rxChannels.append(rxChannel)
        return rxChannels

    def getAllChannels(self):
        return self.getPairingChannels() + self.getCommunicationChannels()

    def onMessageReceived(self, channel, msgType, encMessage):
        if channel in self.connections:
            connection = self.connections[channel]
        elif self.tempConnection is not None and self.tempConnection.pubKey is not None:
            connection = self.tempConnection
        else:
            connection = None
        message = EncryptionHelper.decrypt(encMessage, connection, self.keyPair[1])

        if msgType == MsgType.PairRequest:
            self.onPairRequestReceived(message)
        elif msgType == MsgType.PairConfirm:
            self.onReceivePairConfirmation(channel, message)
        elif msgType == MsgType.TextMessage:
            self.printMessageCallback(message, msgType)

    def onReceivePairConfirmation(self, channel, message):
        print("Received a pairing confirmation")
        pairConfirm = pb_msg.PairConfirm()
        pairConfirm.ParseFromString(message)
        self.tempConnection.txChannel = pairConfirm.receiving_topic
        self.addConnection(self.tempConnection)

    def onPairRequestReceived(self, message):
        print("Received a pair request")
        pairRequest = pb_msg.PairRequest()
        pairRequest.ParseFromString(message)
        txChannel = pairRequest.receiving_topic
        rxChannel = getChannelId()
        connection = self.addConnection(Connection(rxChannel, txChannel, pairRequest.pub_key))
        pairConfirm = pb_msg.PairConfirm()
        pairConfirm.receiving_topic = rxChannel
        serializedMessage = pairConfirm.SerializeToString()
        self.send(connection, serializedMessage, MsgType.PairConfirm)

    def getPublicKey(self):
        return str(self.keyPair[0].decode("utf-8"))

    def openForPairRequests(self):
        print("Open for pair requests")
        pairChannelId = getChannelId()
        self.subscribeToPairingChannel(pairChannelId)
        return pairChannelId

    def pair(self, txPairChannel, pubKey):
        print("Pairing with: " + txPairChannel)
        rxChannel = getChannelId()
        self.subscribeToPairingChannel(rxChannel)
        pairRequest = pb_msg.PairRequest()
        pairRequest.receiving_topic = rxChannel
        pairRequest.pub_key = self.getPublicKey()
        pairRequestMessage = pairRequest.SerializeToString()
        self.tempConnection = Connection(rxChannel, txPairChannel, pubKey)
        self.send(self.tempConnection, pairRequestMessage, MsgType.PairRequest)

    def sendTextMessage(self, connection, textMessage):
        msg = pb_msg.TextMessage()
        msg.content = textMessage
        serializedMessage = msg.SerializeToString()
        self.send(connection, serializedMessage, MsgType.TextMessage)

    def send(self, connection, serializedMessage, msgType):
        data = EncryptionHelper.encrypt(serializedMessage, connection, self.keyPair[1])
        self.mqttConnector.publish(connection.txChannel, data, msgType)

    def subscribeToPairingChannel(self, pairingChannel):
        print("Subscribing to pairing channel=" + pairingChannel)
        self.pairingChannels.append(pairingChannel)
        self.updateSubscriptions()

    def updateSubscriptions(self):
        channels = self.getAllChannels()
        self.mqttConnector.updateSubscriptions(channels)

    def addConnection(self, connection):
        self.connections[connection.rxChannel] = connection
        print("A new connection has been added. \n"
              "RxChannel=" + connection.rxChannel + "\n"
                                                    "TxChannel=" + connection.txChannel + "\n"
                                                                                          "TxPubKey=" + connection.pubKey)
        self.updateSubscriptions()
        return connection
