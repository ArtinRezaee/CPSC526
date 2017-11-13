import socket
import os
import random
import string
import hashlib
import sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

#Function to generate the initialization vector and session key
def initConnection(cipher_type):
    global key,nonce,iv,sess_key
    # Create a initialization vector using the key and nonce
    iv = hashlib.sha256((key + nonce + "IV").encode('utf-8')).digest()[:16]
    # Create a session key based on the cipher type using the key and nonce
    if(cipher_type == 'aes128'):
        sess_key = hashlib.sha256((key + nonce + "SK").encode('utf-8')).digest()[:16]
    elif(cipher_type == 'aes256'):
        sess_key = hashlib.sha256((key + nonce + "SK").encode('utf-8')).digest()

# Function to send encrypted messages to the server
def send(msg, cipher_type):
    global key, nonce, client
    
    # send the raw message to the server if there is no cipher specified
    if(cipher_type == 'null'):
        client.sendall(msg.encode('utf-8'))
    else:
        # padd the message
        padder = padding.PKCS7(128).padder()
        padded_msg = padder.update(msg.encode('utf-8')) + padder.finalize()
        # encrypt the padded message with the specified cipher type
        backend = default_backend()
        cipher = Cipher(algorithms.AES(sess_key), modes.CBC(iv), backend=backend)
        encryptor = cipher.encryptor()
        encrypted_msg = encryptor.update(padded_msg) + encryptor.finalize()
        
        # Send encrypted message to the server
        client.sendall(encrypted_msg)

# Function to receive encrypted messages from the server and decrypt it for the client's use
def recv(size, cipher_type):
    global key, nonce, client
    
    # Only decode if cipher is null
    if(cipher_type == 'null'):
        msg = client.recv(size).decode('utf-8')
    
    #based on the type of cipher
    elif(cipher_type == 'aes128'):
        
        # receive the data from client
        data = client.recv(size)

        # decrypt the data
        backend = default_backend()
        
        cipher = Cipher(algorithms.AES(sess_key), modes.CBC(iv), backend=backend)
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(data) + decryptor.finalize()
        
        # Unpad the data and return the message
        unpadder = padding.PKCS7(128).unpadder()
        unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
        msg = unpadded_data.decode('utf-8')

    # Same as above
    elif(cipher_type == 'aes256'):
        data = client.recv(size)

        backend = default_backend()

        cipher = Cipher(algorithms.AES(sess_key), modes.CBC(iv), backend=backend)
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(data) + decryptor.finalize()
        
        unpadder = padding.PKCS7(128).unpadder()
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
    
    # Get the commands needed for the program's execution
    if(len(sys.argv) == 6):
        command = sys.argv[1]
        filename = sys.argv[2]
        destination = sys.argv[3]
        cipher = sys.argv[4]
        key = sys.argv[5]

        host, port = destination.split(':')

        # Create the socket and connect to it
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host,int(port)))
        
        # Generate a random 16 byte nonce
        nonce = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))
        
        # Initialize the connection
        initConnection(cipher)
        
        # Send the first message to the server
        client.sendall((cipher + "," + nonce).encode('utf-8'))
        
        # Receive challenge from client
        data = recv(128, cipher)
        
        # Create a hash and prove to the server that you have the knowledge of the key
        auth_data = (data + key).encode('utf-8')
        msg = hashlib.sha256(auth_data).hexdigest()
        send(msg, cipher)
        
        # Get server's response and print
        result = recv(128, cipher)
        print(result)

        # Send the command along with filename to server
        send(command + "," + filename, cipher)
        
        # Get servers response
        result = recv(128, cipher)
        if(result == "OK got your command"):
            if(command == "read"):
                # Read the information sent by the server and write it to an standard output
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
                # Read the information from standard input and send it to the server
                for line in sys.stdin:
                    send(line, cipher)
                    response = recv(128, cipher)
                    if(response != line):
                        print("Something went wrong")
                        break
                send("OK", cipher)
                result = recv(128, cipher)    
                if(result == "OK"):
                    print("File successfully uploaded.")
                else:
                    print(result)
        else:
            pass
