from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
import gen.messages_pb2 as pb_msg

"""
Documentation at:
https://pycryptodome.readthedocs.io/en/latest/src/examples.html#encrypt-data-with-rsa
"""


def encrypt(message, pubKey):
    session_key = get_random_bytes(16)
    cipher_rsa = PKCS1_OAEP.new(RSA.import_key(pubKey))
    enc_session_key = cipher_rsa.encrypt(session_key)
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(message)
    encryptedMsg = pb_msg.EncryptionWrapper()
    encryptedMsg.encrypted_session_key = enc_session_key
    encryptedMsg.nonce = cipher_aes.nonce
    encryptedMsg.tag = tag
    encryptedMsg.cipher_text = ciphertext
    data = encryptedMsg.SerializeToString()

    return data


def decrypt(encMessage, privateKey):
    encryptedMsg = pb_msg.EncryptionWrapper()
    encryptedMsg.ParseFromString(encMessage)
    enc_session_key = encryptedMsg.encrypted_session_key
    nonce = encryptedMsg.nonce
    tag = encryptedMsg.tag
    ciphertext = encryptedMsg.cipher_text

    cipher_rsa = PKCS1_OAEP.new(RSA.import_key(privateKey))
    session_key = cipher_rsa.decrypt(enc_session_key)

    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    message = cipher_aes.decrypt_and_verify(ciphertext, tag)
    return message
