import socketserver
import socket
import sys
import hashlib
import random
import time
import os
import string
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from socket import gethostname, gethostbyname

def initConnection(cipher_type):
    global key,nonce,iv,sess_key
    iv = hashlib.sha256((key + nonce + "IV").encode('utf-8')).digest()[:16]
    if(cipher_type == 'aes128'):
        sess_key = hashlib.sha256((key + nonce + "SK").encode('utf-8')).digest()[:16]
    elif(cipher_type == 'aes256'):
        sess_key = hashlib.sha256((key + nonce + "SK").encode('utf-8')).digest()
    print(time.strftime("%Y-%m-%d %H:%M"),": IV="+str(iv))
    print(time.strftime("%Y-%m-%d %H:%M"),": SK="+str(sess_key))


def send(msg, cipher_type):
    global key, nonce, client_socket, sess_key, iv
    if(cipher_type == 'null'):
        client_socket.send(msg.encode('utf-8'))
    else:
#        if(cipher_type == 'aes128'):
#            sess_key = hashlib.sha256((key + nonce + "SK").encode('utf-8')).digest()[:16]
#        elif(cipher_type == 'aes256'):
#            sess_key = hashlib.sha256((key + nonce + "SK").encode('utf-8')).digest()

        padder = padding.PKCS7(128).padder()
        padded_msg = padder.update(msg.encode('utf-8')) + padder.finalize()

#        iv = hashlib.sha256((key + nonce + "IV").encode('utf-8')).digest()[:16]
        backend = default_backend()
        cipher = Cipher(algorithms.AES(sess_key), modes.CBC(iv), backend=backend)
        encryptor = cipher.encryptor()
        encrypted_msg = encryptor.update(padded_msg) + encryptor.finalize()
    
        client_socket.send(encrypted_msg)


def recv(size, cipher_type):
    global key, nonce, client_socket
    if(cipher_type == 'null'):
        msg = client_socket.recv(size).decode('utf-8')
    
    elif(cipher_type == 'aes128'):
        
        data = client_socket.recv(size)
        
#        iv = hashlib.sha256((key + nonce + "IV").encode('utf-8')).digest()[:16]
#        sess_key = hashlib.sha256((key + nonce + "SK").encode('utf-8')).digest()[:16]
        backend = default_backend()
        
        cipher = Cipher(algorithms.AES(sess_key), modes.CBC(iv), backend=backend)
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(data) + decryptor.finalize()
        
        unpadder = padding.PKCS7(128).unpadder()
        unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
        msg = unpadded_data.decode('utf-8')

    elif(cipher_type == 'aes256'):
        data = client_socket.recv(size)
        
#        iv = hashlib.sha256((key + nonce + "IV").encode('utf-8')).digest()[:16]
#        sess_key = hashlib.sha256((key + nonce + "SK").encode('utf-8')).digest()
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


iv = None
sess_key = None
if __name__ == "__main__":
    HOST, PORT, key = "localhost", int(sys.argv[1]), sys.argv[2]
    # Boolan to see if user is logged in
    loggedIn = False;
    # Boolean to see if server has gotten a command
    gotCommand = False;
    # Create a socket that can handle nc command
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Bind to the host and port and start listening
        server.bind((HOST, PORT))
        server.listen(0)
        print("Listening on port "+str(PORT))
        print("Using secret key: "+key)
    except socket.error as e:
        if e.errno == 98:
            print("Port is already in use")

    while True:
        # Accept new clients and prompt them to login
        client_socket, info= server.accept()
        data = client_socket.recv(128).decode('utf8').strip()
        cipher,nonce = data.split(',')
        auth_token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))
        print(time.strftime("%Y-%m-%d %H:%M"),": New Connection from "+ client_socket.getpeername()[0] + " cipher="+cipher)
        print(time.strftime("%Y-%m-%d %H:%M"),": nonce="+nonce)
        initConnection(cipher)
        send(auth_token, cipher)

        while True:
            # Recieve data from client
            data = recv(128,cipher)
#            print(data)
            if not loggedIn:
                hash_auth = hashlib.sha256()
                hash_auth.update((auth_token+key).encode('utf-8'))
                # Check user's credintials
                if hash_auth.hexdigest() == data:
                    loggedIn = True
                    # Prompt user to enter a command
                    send('Welcome to the back-door server\n', cipher)
                else:
                    # Terminate client socket if wrong password is inputted
                    send('Wrong password! bye\n', cipher)
                    client_socket.close()
                    break
            else:
                if not gotCommand:
                    gotCommand = True
                    command = data
                    send("OK got your command",cipher)
                else:
                    if command == 'read':
                        print(time.strftime("%Y-%m-%d %H:%M"),": command:"+command+ ", filename:"+data)
                        send("OK downloading "+data,cipher)
                    elif command == 'write':
                        print(time.strftime("%Y-%m-%d %H:%M"),": command:"+command+ ", filename:"+data)
                        send("OK uploading "+data,cipher)
    

#                # Interpret user info by matching it with one of the definitions in the variable
#                args = data.split()
#                if args[0] == "off":
#                    do_off(server,client_socket,args)
#                elif args[0] == "logout":
#                    do_logout(client_socket,args)
#                    loggedIn = False
#                    break
#                else:
#                    if not args[0] in interpretInput:
#                        client_socket.send(b'\033[91mNo such command\n\033[0m')
#                    else:
#                        interpretInput[args[0]](client_socket,args)

    # close clients socket
    client_socket.close()
    # close the server socket
    server.close()
    # terminate the program
    sys.exit()




