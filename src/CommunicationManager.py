from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA

from CommunicationHelper import generateKeyPair, getMsgType, MsgType, getChannelId
from Connection import Connection
from MqttConnector import MqttConnector
import gen.messages_pb2 as pb_msg


class CommunicationManager:

    def __init__(self, onPrintMessageReceivedCallback):
        self.printMessageCallback = onPrintMessageReceivedCallback
        self.keyPair = self.getKeyPair()
        self.ongoingPairingRxPubKey = None
        self.mqttConnector = MqttConnector(self.onMessageReceived)
        self.connections = {}
        self.pairingChannels = []

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
        enc_session_key, nonce, tag, ciphertext = \
            [encMessage.read(x) for x in (self.keyPair[1].size_in_bytes(), 16, 16, -1)]

        cipher_rsa = PKCS1_OAEP.new(RSA.import_key(self.keyPair[1]))
        session_key = cipher_rsa.decrypt(enc_session_key)

        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        message = cipher_aes.decrypt_and_verify(ciphertext, tag)

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
        txChannel = pairConfirm.receiving_topic
        rxChannel = channel
        self.addConnection(rxChannel, txChannel,
                           self.ongoingPairingRxPubKey)  # ToDo missing pubkey - must be receieved during pair

    def onPairRequestReceived(self, message):
        print("Received a pair request")
        pairRequest = pb_msg.PairRequest()
        pairRequest.ParseFromString(message)
        txChannel = pairRequest.receiving_topic
        rxChannel = getChannelId()
        self.addConnection(rxChannel, txChannel, pairRequest.pubKey)
        pairConfirm = pb_msg.PairConfirm()
        pairConfirm.receiving_topic = rxChannel
        serializedMessage = pairConfirm.SerializeToString()
        tempConnection = Connection(rxChannel, txChannel, pairRequest.pubKey)
        self.send(tempConnection, serializedMessage, MsgType.PairConfirm)

    def getPublicKey(self):
        return str(self.keyPair[0].decode("utf-8"))

    def openForPairRequests(self):
        print("Open for pair requests")
        pairChannelId = getChannelId()
        self.subscribeToPairingChannel(pairChannelId)
        return pairChannelId

    def pair(self, pairId, pubKey):
        print("Pairing with: " + pairId)
        self.ongoingPairingRxPubKey = pubKey
        rxChannel = getChannelId()
        self.subscribeToPairingChannel(rxChannel)
        pairRequest = pb_msg.PairRequest()
        pairRequest.receiving_topic = rxChannel
        pairRequest.pubKey = self.getPublicKey()
        pairRequestMessage = pairRequest.SerializeToString()
        tempConnection = Connection(rxChannel, pairId, pubKey)
        self.send(tempConnection, pairRequestMessage, MsgType.PairRequest)

    def sendTextMessage(self, connection, textMessage):
        msg = pb_msg.TextMessage()
        msg.content = textMessage
        serializedMessage = msg.SerializeToString()
        self.send(connection, serializedMessage, MsgType.TextMessage)

    def send(self, connection, serializedMessage, msgType):
        session_key = get_random_bytes(16)
        cipher_rsa = PKCS1_OAEP.new(RSA.import_key(connection.pubKey))
        enc_session_key = cipher_rsa.encrypt(session_key)
        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(serializedMessage)
        self.mqttConnector.publish(connection.txChannel, (enc_session_key, cipher_aes.nonce, tag, ciphertext), msgType)

    def subscribeToPairingChannel(self, pairingChannel):
        print("Subscribing to pairing channel=" + pairingChannel)
        self.pairingChannels.append(pairingChannel)
        self.updateSubscriptions()

    def updateSubscriptions(self):
        channels = self.getAllChannels()
        self.mqttConnector.updateSubscriptions(channels)

    def addConnection(self, rxChannel, txChannel, pubKeyClient):
        connection = Connection(rxChannel, txChannel, pubKeyClient)
        self.connections[rxChannel] = connection
        print("A new connection has been added. \n"
              "RxChannel=" + connection.rxChannel + "\n"
                                                    "TxChannel=" + connection.txChannel + "\n"
                                                                                          "TxPubKey=" + connection.pubKey)
        self.updateSubscriptions()
