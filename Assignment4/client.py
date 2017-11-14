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
def initCipherValues(cipher_type):
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
    global key, nonce, client_socket, sess_key, iv
    # send the raw message to the client if there is no cipher specifies
    if(cipher_type == 'null'):
        client_socket.send(msg.encode('utf-8'))
    else:
        n = 16
        blocks = [msg[i:i+n] for i in range(0, len(msg), n)]

        for block in blocks:
            # padd the message
            if(len(block) < 16):
                padder = padding.PKCS7(128).padder()
                padded_msg = padder.update(block.encode('utf-8')) + padder.finalize()
            else:
                padded_msg = block.encode('utf-8')
            # encrypt the padded message with the specified cipher type
            backend = default_backend()
            cipher = Cipher(algorithms.AES(sess_key), modes.CBC(iv), backend=backend)
            encryptor = cipher.encryptor()
            encrypted_msg = encryptor.update(padded_msg) + encryptor.finalize()
            # Send encrypted message to the server
            client.sendall(encrypted_msg)
        padder = padding.PKCS7(128).padder()
        padded_msg = padder.update(("OK").encode('utf-8')) + padder.finalize()
        # encrypt the padded message with the specified cipher type
        backend = default_backend()
        cipher = Cipher(algorithms.AES(sess_key), modes.CBC(iv), backend=backend)
        encryptor = cipher.encryptor()
        encrypted_msg = encryptor.update(padded_msg) + encryptor.finalize()
        client.sendall(encrypted_msg)

def sendData(msg, cipher_type):
    global key, nonce, client_socket, sess_key, iv
    # send the raw message to the client if there is no cipher specifies
    if(cipher_type == 'null'):
        client.send(msg.encode('utf-8'))
    else:
        n = 16
        blocks = [msg[i:i+n] for i in range(0, len(msg), n)]

        for block in blocks:
            # padd the message
            if(len(block) < 16):
                padder = padding.PKCS7(128).padder()
                padded_msg = padder.update(block.encode('utf-8')) + padder.finalize()
            else:
                padded_msg = block.encode('utf-8')
            # encrypt the padded message with the specified cipher type
            backend = default_backend()
            cipher = Cipher(algorithms.AES(sess_key), modes.CBC(iv), backend=backend)
            encryptor = cipher.encryptor()
            encrypted_msg = encryptor.update(padded_msg) + encryptor.finalize()
            
            # Send encrypted message to the server
            client.sendall(encrypted_msg)

# Function to receive encrypted messages from the server and decrypt it for the client's use
def recv(size, cipher_type):
    size = 16
    global key, nonce, client
    tot_msg = ""
    # Only decode if cipher is null
    if(cipher_type == 'null'):
        msg = client.recv(size).decode('utf-8')
    #based on the type of cipher
    else:
        while True:
            data = client.recv(size)
            backend = default_backend()

            cipher = Cipher(algorithms.AES(sess_key), modes.CBC(iv), backend=backend)
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(data) + decryptor.finalize()
            try:
                unpadder = padding.PKCS7(128).unpadder()
                unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
            except ValueError:
                unpadded_data = decrypted_data
            msg = unpadded_data.decode('utf-8')
            if(msg == "OK"):
                break
            tot_msg += msg
    return tot_msg

def recvData(size, cipher_type):
    size = 16
    global key, nonce, client
    # Only decode if cipher is null
    if(cipher_type == 'null'):
        msg = client.recv(size).decode('utf-8')
    #based on the type of cipher
    else:
        data = client.recv(size)
        backend = default_backend()

        cipher = Cipher(algorithms.AES(sess_key), modes.CBC(iv), backend=backend)
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(data) + decryptor.finalize()
        try:
            unpadder = padding.PKCS7(128).unpadder()
            unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
        except ValueError:
            unpadded_data = decrypted_data
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
        if((command != "read") and (command != "write")):
            print("Invalid command. Please use one of the following:\nread\nwrite\nProgram exiting...", file=sys.stderr)
            sys.exit()
        
        if((cipher != "null") and (cipher != "aes128") and (cipher != "aes256")):
            print("Invalid cipher. Please use one of the following:\nnull\naes128\naes256\nProgram exiting...", file=sys.stderr)
            sys.exit()
        
        if((command == "write") and (sys.stdin.isatty())):
            print("No input for write detected. Exiting...", file=sys.stderr)
            sys.exit()
        
        host, port = destination.split(':')

        # Create the socket and connect to it
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host,int(port)))
        
        # Generate a random 16 byte nonce
        nonce = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))
        
        # Initialize the connection
        initCipherValues(cipher)
        
        # Send the first message to the server
        client.sendall((cipher + "," + nonce).encode('utf-8'))
        
        # Receive challenge from client
        data = recv(16, cipher)
        
        # Create a hash and prove to the server that you have the knowledge of the key
        auth_data = (data + key).encode('utf-8')
        hash_auth = hashlib.sha256(auth_data).hexdigest()
        send(hash_auth, cipher)
        
        # Get server's response and print
        result = recv(128, cipher)
        print(result, file=sys.stderr)

        # Send the command along with filename to server
        send(command + "," + filename, cipher)
        
        # Get servers response
        result = recv(128, cipher)
        if(result == "OK got your command"):
            if(command == "read"):
                # Read the information sent by the server and write it to an standard output
                while True:
                    result = recvData(128, cipher)
                    if(result == "Error: FDNE"):
                        print("File could not be successfully downloaded. Program Exiting...", file=sys.stderr)
                        sys.exit()
                    elif(result == "Done"):
                        print("File successfully downloaded.", file=sys.stderr)
                        sys.exit()
                    else:
                        print(result, end='')
            elif(command == "write"):
                # Read the information from standard input and send it to the server
                for line in sys.stdin:
                    sendData(line, cipher)
                sendData("Done", cipher)
                result = recv(128, cipher)    
                if(result == "Done"):
                    print("File successfully uploaded.", file=sys.stderr)
                else:
                    print("File could not be successfully uploaded. Program Exiting...", file=sys.stderr)
        else:
            pass
