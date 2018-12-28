import unittest

import CommunicationHelper
from CommunicationManager import CommunicationManager
from time import sleep
import gen.messages_pb2 as pb_msg


class Tests(unittest.TestCase):



    def testPairing(self):
        # Start client1 and open for pairing
        fax = CommunicationManager(self.onTestMsgReceived)
        sleep(2)
        pubKeyFax = fax.getPublicKey()
        pairingId = fax.openForPairRequests()

        remote = CommunicationManager(self.onTestMsgReceived)
        pubKeyRemote = remote.getPublicKey()
        remote.pair(pairingId, pubKeyFax)
        sleep(2)

        for key, value in fax.connections.items():
            faxConnection = value


        for key, value in remote.connections.items():
            remoteConnection = value


        txFax = faxConnection.txChannel
        rxRemote = remoteConnection.rxChannel

        rxFax = faxConnection.rxChannel
        txRemote = remoteConnection.txChannel

        self.assertEqual(rxFax, txRemote)
        self.assertEqual(txFax, rxRemote)

        self.assertEqual(pubKeyFax, remoteConnection.pubKey)
        self.assertEqual(pubKeyRemote, faxConnection.pubKey)

    def testMessage(self):
        # Start client1 and open for pairing
        fax = CommunicationManager(self.onTestMsgReceived)
        sleep(2)
        pubKeyFax = fax.getPublicKey()
        pairingId = fax.openForPairRequests()

        remote = CommunicationManager(None)
        remote.pair(pairingId, pubKeyFax)

        sleep(2)

        for key, value in remote.connections.items():
            remoteConnection = value

        textSent = "Hello World"
        remote.sendTextMessage(remoteConnection, textSent)
        sleep(2)
        self.assertEqual(textSent, self.textReceived)



    def onTestMsgReceived(self, message, msgType):
        if(msgType == CommunicationHelper.MsgType.TextMessage):
            textMessage = pb_msg.TextMessage()
            textMessage = textMessage.ParseFromString(message)
            self.textReceived = textMessage.message
    #
    #




if __name__ == '__main__':
    unittest.main()