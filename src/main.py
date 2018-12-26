from time import sleep
from CommunicationManager import CommunicationManager


def printPairingQR(pairingId):
    print("Now listening for new paring on: " + pairingId)


comms = CommunicationManager()
sleep(2)
pairingId = comms.openNewPairing()
printPairingQR(pairingId)

while True:
    sleep(120)
