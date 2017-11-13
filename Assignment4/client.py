import socket
import os
import random
import string
import hashlib
import sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

def initConnection(cipher_type):
    global key,nonce,iv,sess_key
    iv = hashlib.sha256((key + nonce + "IV").encode('utf-8')).digest()[:16]
    if(cipher_type == 'aes128'):
        sess_key = hashlib.sha256((key + nonce + "SK").encode('utf-8')).digest()[:16]
    elif(cipher_type == 'aes256'):
        sess_key = hashlib.sha256((key + nonce + "SK").encode('utf-8')).digest()

def send(msg, cipher_type):
    global key, nonce, client
    if(cipher_type == 'null'):
        client.sendall(msg.encode('utf-8'))
    else:
        # if(cipher_type == 'aes128'):
        #     sess_key = hashlib.sha256((key + nonce + "SK").encode('utf-8')).digest()[:16]
        # elif(cipher_type == 'aes256'):
        #     sess_key = hashlib.sha256((key + nonce + "SK").encode('utf-8')).digest()

        padder = padding.PKCS7(128).padder()
        padded_msg = padder.update(msg.encode('utf-8')) + padder.finalize()

        # iv = hashlib.sha256((key + nonce + "IV").encode('utf-8')).digest()[:16]
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
        data = client.recv(size)
#        print(data)

        # iv = hashlib.sha256((key + nonce + "IV").encode('utf-8')).digest()[:16]
        # sess_key = hashlib.sha256((key + nonce + "SK").encode('utf-8')).digest()[:16]
        backend = default_backend()
        
        cipher = Cipher(algorithms.AES(sess_key), modes.CBC(iv), backend=backend)
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(data) + decryptor.finalize()
        
        unpadder = padding.PKCS7(128).unpadder()
#        print("decrypted_data:" + str(decrypted_data))
        unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
        msg = unpadded_data.decode('utf-8')
    elif(cipher_type == 'aes256'):
        data = client.recv(size)
#        print(data)

        # iv = hashlib.sha256((key + nonce + "IV").encode('utf-8')).digest()[:16]
        # sess_key = hashlib.sha256((key + nonce + "SK").encode('utf-8')).digest()
        backend = default_backend()

        cipher = Cipher(algorithms.AES(sess_key), modes.CBC(iv), backend=backend)
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(data) + decryptor.finalize()
        
        print("server said:" + str(decrypted_data))
        unpadder = padding.PKCS7(128).unpadder()
#        print("decrypted_data:" + str(decrypted_data))
        unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
        msg = unpadded_data.decode('utf-8')
    return msg

def encrypt(msg):
    pass

key = None
nonce = None
client = None
iv = None
sess_key = None
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
        initConnection(cipher)
        client.sendall((cipher + "," + nonce).encode('utf-8'))

        data = recv(128, cipher)
        #data = client.recv(128).decode('utf-8')
        auth_data = (data + key).encode('utf-8')
        msg = hashlib.sha256(auth_data).hexdigest()
        send(msg, cipher)
        #client.sendall(msg.encode('utf-8'))
        result = recv(128, cipher)
        print(result)

        send(command + "," + filename, cipher)
        result = recv(128, cipher)
        if(result == "OK got your command"):
            if(command == "read"):
                while True:
                    result = recv(128, cipher)
                    send(result, cipher)
                    if(result == "Something went wrong"):
                        print(result)
                        break
                    elif(result == "OK"):
                        print("File successfully downloaded.")
                        break
                    else:
                        print(result)
            elif(command == "write"):
                for line in sys.stdin:
                    send(line, cipher)
                    response = recv(128, cipher)
                    if(response != line):
                        print("Something went wrong")
                        break
                result = recv(128, cipher)    
                if(result == "Ok"):
                    print("File successfully uploaded.")
                else:
                    print(result)
        else:
            pass
        #client.sendall((command + "," + filename).encode('utf-8'))
