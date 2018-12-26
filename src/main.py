from time import sleep
from CommunicationManager import CommunicationManager


def printPairingQR(pairingId):
    print("Now listening for new paring on: " + pairingId)


communicationManager = CommunicationManager()
sleep(2)
pairingId = communicationManager.openForPairRequests()
printPairingQR(pairingId)

while True:
    sleep(120)
