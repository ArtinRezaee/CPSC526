import socket
import os
import random
import string
import hashlib
import sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding


def send(msg, cipher_type):
    global key, nonce, client
    if(cipher_type == 'null'):
        client.sendall(msg.encode('utf-8'))
    
    elif(cipher_type == 'aes128'):
        pass
    elif(cipher_type == 'aes256'):
        padder = padding.PKCS7(128).padder()
        padded_msg = padder.update(msg.encode('utf-8')) + padder.finalize()
        
        iv = hashlib.sha256((key + nonce + "IV").encode('utf-8')).digest()[:16]
        sess_key = hashlib.sha256((key + nonce + "SK").encode('utf-8')).digest()
        backend = default_backend()
        cipher = Cipher(algorithms.AES(sess_key), modes.CBC(iv), backend=backend)
        encryptor = cipher.encryptor()
        encrypted_msg = encryptor.update(padded_msg) + encryptor.finalize()
        
        client.sendall(encrypted_msg)

def recv(size, cipher_type):
    global key, nonce, client
    if(cipher_type == 'null'):
        msg = client.recv(size).decode('utf-8')
    
    elif(cipher_type == 'aes128'):
        pass
    elif(cipher_type == 'aes256'):
        data = client.recv(size)
        print(data)
        
        iv = hashlib.sha256((key + nonce + "IV").encode('utf-8')).digest()[:16]
        sess_key = hashlib.sha256((key + nonce + "SK").encode('utf-8')).digest()
        backend = default_backend()

        cipher = Cipher(algorithms.AES(sess_key), modes.CBC(iv), backend=backend)
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(data) + decryptor.finalize()
        
        unpadder = padding.PKCS7(128).unpadder()
        print("decrypted_data:" + str(decrypted_data))
        unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
        msg = unpadded_data
    return msg

def encrypt(msg):
    pass

key = None
nonce = None
client = None
if __name__ == "__main__":
    if(len(sys.argv) == 6):
#        global key, nonce, client
        command = sys.argv[1]
        filename = sys.argv[2]
        destination = sys.argv[3]
        cipher = sys.argv[4]
        key = sys.argv[5]

        host, port = destination.split(':')

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host,int(port)))
        nonce = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))
        client.sendall((cipher + "," + nonce).encode('utf-8'))

        data = recv(128, cipher).decode('utf-8')
        #data = client.recv(128).decode('utf-8')
        auth_data = (data + key).encode('utf-8')
        msg = hashlib.sha256(auth_data).hexdigest()
        send(msg, cipher)
        #client.sendall(msg.encode('utf-8'))
        result = recv(128, cipher)
        print(result)

        send(command + "," + filename, cipher)
        #client.sendall((command + "," + filename).encode('utf-8'))

'''
backend = default_backend()

cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
encryptor = cipher.encryptor()
ct = encryptor.update(b"a secret message") + encryptor.finalize()


>>> padder = padding.PKCS7(128).padder()
>>> padded_data = padder.update(b"11111111111111112222222222")
>>> padded_data
'1111111111111111'
>>> padded_data += padder.finalize()
>>> padded_data
'11111111111111112222222222\x06\x06\x06\x06\x06\x06'

>>> unpadder = padding.PKCS7(128).unpadder()
>>> data = unpadder.update(padded_data)
>>> data
'1111111111111111'
>>> data + unpadder.finalize()
'11111111111111112222222222'
'''
