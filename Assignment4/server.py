import socketserver
import socket
import sys
import hashlib
import random
import time
import os
import os.path
import string
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

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
    print(time.strftime("%Y-%m-%d %H:%M"),": IV="+str(iv))
    print(time.strftime("%Y-%m-%d %H:%M"),": SK="+str(sess_key))

# Function to send encrypted messages to the client
def send(msg, cipher_type):
    global key, nonce, client_socket, sess_key, iv
    print("Server saying: " + msg)
    # send the raw message to the client if there is no cipher specifies
    if(cipher_type == 'null'):
        client_socket.send(msg.encode('utf-8'))
    else:
        # padd the message
        padder = padding.PKCS7(128).padder()
        padded_msg = padder.update(msg.encode('utf-8')) + padder.finalize()
        # encrypt the padded message with the specified cipher type
        print("server is saying: " + str(padded_msg))
        backend = default_backend()
        cipher = Cipher(algorithms.AES(sess_key), modes.CBC(iv), backend=backend)
        encryptor = cipher.encryptor()
        encrypted_msg = encryptor.update(padded_msg) + encryptor.finalize()
        
        # Send encrypted message to the user
        client_socket.send(encrypted_msg)

# Function to receive encrypted messages from the client and decrypt it for the server's use
def recv(size, cipher_type):
    global key, nonce, client_socket
    
    # Only decode if cipher is null
    if(cipher_type == 'null'):
        msg = client_socket.recv(size).decode('utf-8')
    
    #based on the type of cipher
    elif(cipher_type == 'aes128'):
        
        # receive the data from client
        data = client_socket.recv(size)
        backend = default_backend()
        
        # decrypt the data
        cipher = Cipher(algorithms.AES(sess_key), modes.CBC(iv), backend=backend)
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(data) + decryptor.finalize()
        # Unpad the data and return the message
        unpadder = padding.PKCS7(128).unpadder()
        unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
        msg = unpadded_data.decode('utf-8')

    # Same as above
    elif(cipher_type == 'aes256'):
        data = client_socket.recv(size)
        backend = default_backend()
        
        cipher = Cipher(algorithms.AES(sess_key), modes.CBC(iv), backend=backend)
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(data) + decryptor.finalize()
        
        unpadder = padding.PKCS7(128).unpadder()
        unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
        msg = unpadded_data.decode('utf-8')
    print("Client saying: " + msg)
    return msg

# Function to read from a file and send to user
def read(fileName,cipher_type):
    try:
        # open the file and read line by line and send each line to user by calling recv
        fileObj = open(fileName,"r")
        for line in fileObj:
            send(line,cipher_type)
            response = recv(128, cipher_type)
            if(response != line):
                return False
        print(time.strftime("%Y-%m-%d %H:%M"), ": Status:Success")
        fileObj.close()
        return True

    # If file doesnt exist or there is a problem, let the user know
    except IOError:
        print(time.strftime("%Y-%m-%d %H:%M"), ": Status:Failed")
        fileObj.close()
        return False

# Function to write content received from the client to a file
def write(fileName,cipher_type):
    try:
        # Try opening a file
        fileObj = open(fileName,"w")
        # while there is an input from client, write it to the file
        while True:
            line = recv(128,cipher_type)
            if line == "OK":
                break
            fileObj.write(line)
            send(line, cipher_type)
        print(time.strftime("%Y-%m-%d %H:%M"), ": Status:Success")
        fileObj.close()
        return True

    # If file doesnt exist or there is a problem, let the user know
    except IOError:
        print(time.strftime("%Y-%m-%d %H:%M"), ": Status:Failed")
        fileObj.close()
        return False



def encrypt(msg):
    pass

# Initialization vector and session key variables
iv = None
sess_key = None
hash_auth = None
if __name__ == "__main__":
    HOST, PORT, key = "localhost", int(sys.argv[1]), sys.argv[2]
    # Boolan to see if user is logged in
    loggedIn = False;
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
        
        # receive initial data from the client
        data = client_socket.recv(128).decode('utf-8').strip()
        
        # Get the cipher and nonce from the received data
        cipher,nonce = data.split(',')
        
        # Create an authentication token randomly for authentication purposes
        auth_token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))
        
        # Log key and nonce on the server side
        print(time.strftime("%Y-%m-%d %H:%M"),": New Connection from "+ client_socket.getpeername()[0] + " cipher="+cipher)
        print(time.strftime("%Y-%m-%d %H:%M"),": nonce="+nonce)
        
        # Initialize the connection
        initConnection(cipher)
        
        # Prompt the client for its knowledge of the key
        send(auth_token, cipher)

        while True:
            # Recieve data from client
            data = recv(128,cipher)
            
            # check if user is logged in or not
            if not loggedIn:
                
                # create the expecting user credintials
                hash_auth = hashlib.sha256()
                hash_auth.update((auth_token+key).encode('utf-8'))
                # Check user's credintials
                if hash_auth.hexdigest() == data:
                    loggedIn = True
                    # Prompt user to enter a command
                    send('Welcome to the back-door server\n', cipher)
                else:
                    # Terminate client socket if wrong password is inputted
                    print(time.strftime("%Y-%m-%d %H:%M"),": Error: Bad key")
                    send('Wrong password! bye\n', cipher)
                    client_socket.close()
                    break
            else:
                # Get user command and file name
                    command,fileName = data.split(',')
                    send("OK got your command",cipher)
                    # perform read operation
                    if command == 'read':
                        print(time.strftime("%Y-%m-%d %H:%M"),": command:"+command+ ", filename:"+fileName)
                        stats = read(fileName, cipher)
                    
                    # perform write operation
                    elif command == 'write':
                        print(time.strftime("%Y-%m-%d %H:%M"),": command:"+command+ ", filename:"+data)
                        stats = write(fileName, cipher)
                    
                    # Give user feedback regarding the operation status
                    if stats:
                        send("OK",cipher)
                    else:
                        send("Error: File does not exist or something went wrong",cipher)
                    
                    # Terminate the client
                    break

        # Close client socket and set the login parameter to false
        client_socket.close()
        loggedIn = False

    # close clients socket
    client_socket.close()
    # close the server socket
    server.close()
    # terminate the program
    sys.exit()




