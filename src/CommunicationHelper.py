import uuid
from enum import Enum, auto

from Crypto.PublicKey import RSA


class MsgType(Enum):
    PairRequest = auto()
    PairConfirm = auto()
    getInfo = auto()
    FaxInfo = auto()
    ClientInfo = auto()
    TextMessage = auto()


stringToType = {"PAIR_REQUEST": MsgType.PairRequest,
                "PAIR_CONFIRM": MsgType.PairConfirm,
                "GET_INFO": MsgType.getInfo,
                "FAX_INFO": MsgType.FaxInfo,
                "CLIENT_INFO": MsgType.ClientInfo,
                "TEXT_MESSAGE": MsgType.TextMessage
                }

typeToString = {MsgType.PairRequest: "PAIR_REQUEST",
                MsgType.PairConfirm: "PAIR_CONFIRM",
                MsgType.getInfo: "GET_INFO",
                MsgType.FaxInfo: "FAX_INFO",
                MsgType.ClientInfo: "CLIENT_INFO",
                MsgType.TextMessage: "TEXT_MESSAGE"
                }


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


def getMsgType(stringType):
    return stringToType[stringType]


def getMsgStringType(msgType):
    return typeToString[msgType]

