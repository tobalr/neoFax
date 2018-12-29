from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Signature import pss
from Crypto.Hash import SHA256
import gen.messages_pb2 as pb_msg


"""
Documentation at:
https://pycryptodome.readthedocs.io/en/latest/src/examples.html#encrypt-data-with-rsa
"""


def encrypt(message, connection, privateKey):
    session_key = get_random_bytes(16)
    cipher_rsa = PKCS1_OAEP.new(RSA.import_key(connection.pubKey))
    enc_session_key = cipher_rsa.encrypt(session_key)
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(message)
    encryptedMsg = pb_msg.EncryptionWrapper()
    encryptedMsg.encrypted_session_key = enc_session_key
    encryptedMsg.nonce = cipher_aes.nonce
    encryptedMsg.tag = tag
    encryptedMsg.cipher_text = ciphertext
    signature = getSignature(ciphertext, privateKey)
    print("signature:" + str(signature))
    encryptedMsg.signature = signature

    data = encryptedMsg.SerializeToString()

    return data


def decrypt(encMessage, connection, privateKey):
    encryptedMsg = pb_msg.EncryptionWrapper()
    encryptedMsg.ParseFromString(encMessage)
    enc_session_key = encryptedMsg.encrypted_session_key
    nonce = encryptedMsg.nonce
    tag = encryptedMsg.tag
    ciphertext = encryptedMsg.cipher_text

    if connection is None:
        isVerified = False
    else:
        signature = encryptedMsg.signature
        isVerified = verify(ciphertext, signature, connection.pubKey)
    print("Is verified [" + str(isVerified) + "]")

    cipher_rsa = PKCS1_OAEP.new(RSA.import_key(privateKey))
    session_key = cipher_rsa.decrypt(enc_session_key)
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)

    message = cipher_aes.decrypt_and_verify(ciphertext, tag)
    return message


def getSignature(cipherText, privateKey):
    key = RSA.import_key(privateKey)
    h = SHA256.new(cipherText)
    signature = pss.new(key).sign(h)
    return signature


def verify(ciperText, signature, pubKey):
    key = RSA.import_key(pubKey)
    h = SHA256.new(ciperText)
    verifier = pss.new(key)
    try:
        verifier.verify(h, signature)
        return True
    except ValueError:
        return False

