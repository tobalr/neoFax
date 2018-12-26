import uuid
from enum import Enum, auto

from Crypto.PublicKey import RSA


class CommType(Enum):
    PairRequest = auto()
    PairConfirm = auto()
    getInfo = auto()
    FaxInfo = auto()
    ClientInfo = auto()
    TextMessage = auto()


def generateKeyPair():
    key = RSA.generate(2048)
    private_key = key.export_key()
    # file_out = open("private.pem", "wb")
    # file_out.write(private_key)

    public_key = key.publickey().export_key()
    # file_out = open("receiver.pem", "wb")
    # file_out.write(public_key)
    return public_key, private_key


def getChannelId():
    return str(uuid.uuid4())


def getCommType(topic):
    return CommType.PairRequest
