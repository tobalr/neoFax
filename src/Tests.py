import unittest

from CommunicationManager import CommunicationManager
from time import sleep


class Tests(unittest.TestCase):

    def testPairing(self):
        # Start client1 and open for pairing
        fax = CommunicationManager()
        sleep(2)
        pubKeyFax = fax.getPublicKey()
        pairingId = fax.openForPairRequests()

        remote = CommunicationManager()
        remote.pair(pairingId, pubKeyFax)
        sleep(20)

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

        self.assertEqual(fax.getPublicKey(), remoteConnection.pubKey)
        self.assertEqual(remote.getPublicKey(), pubKeyFax)

if __name__ == '__main__':
    unittest.main()