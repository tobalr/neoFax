import unittest

from CommunicationManager import CommunicationManager
from time import sleep


class Tests(unittest.TestCase):

    def testPairing(self):
        # Start client1 and open for pairing
        fax = CommunicationManager()
        sleep(2)
        pairingId = fax.openForPairRequests()

        remote = CommunicationManager()
        remote.pair(pairingId)
        sleep(20)

        for key, value in fax.connections.items():
            faxConnection = value


        for key, value in remote.connections.items():
            remoteConnection = value


        txFax = faxConnection.txChannel
        rxRemote = remoteConnection.rxChannel

        rxFax = faxConnection.rxChannel
        txRemote = remoteConnection.txChannel

        self.assertEqual(rxFax, txRemote);
        self.assertEqual(txFax, rxRemote);

    # def test_upper(self):
    #     self.assertEqual('foo'.upper(), 'FOO')
    #
    # def test_isupper(self):
    #     self.assertTrue('FOO'.isupper())
    #     self.assertFalse('Foo'.isupper())
    #
    # def test_split(self):
    #     s = 'hello world'
    #     self.assertEqual(s.split(), ['hello', 'world'])
    #     # check that s.split fails when the separator is not a string
    #     with self.assertRaises(TypeError):
    #         s.split(2)

if __name__ == '__main__':
    unittest.main()