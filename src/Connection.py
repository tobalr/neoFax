class Connection:
    """Represents one connection to a remote peer.
    RxChannel is used for receiving.
    TxChannel is used for sending.
    PubKey is used for encrypting sent msgs."""

    def __init__(self, rxChannel, txChannel, pubKey):
        self.rxChannel = rxChannel
        self.txChannel = txChannel
        self.pubKey = pubKey
