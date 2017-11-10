import socketserver
import socket
import sys
import hashlib
import random
import string
from Crypto.Cipher import AES
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

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
    except socket.error as e:
        if e.errno == 98:
            print("Port is already in use")

    try:
        while True:
            # Accept new clients and prompt them to login
            client_socket, info= server.accept()
            data = client_socket.recv(128).decode('utf8').strip()
            cipher,nonce = data.split(',')
            if cipher == 'null':
                auth_token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))
                client_socket.send(auth_token.encode('utf-8'))
            else:
                backend = default_backend()
                IV = None
                SK = None
                if cipher == 'aes128':
                    auth_token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))
                    padder = padding.PKCS7(128).padder()
                    unpadder = padding.PKCS7(128).unpadder()
                    padded_data = padder.update(auth_token.encode('utf-8'))
                    padded_data += padder.finalize()
#                    if len(key) < 16:
#                        padding_needed = 16 - len(key)
#                        new_key = ""
#                        for i in range(16):
#                            if i < len(key)-1:
#                                new_key += key[i]
#                            else:
#                                new_key += str(padding_needed)
#                        key = new_key

                iv = (hashlib().sha256()).update(key+nonce+'IV').digest()
                sk = (hashlib().sha256()).update(key+nonce+'SK').digest()
                crypto = Cipher(algorithms.AES(sk), modes.CBC(iv), backend=backend)
                encryptor = crypto.encryptor()
                decryptor = crypto.decryptor()
                client_socket.send((encryptor.update(padded_data) + encryptor.finalize()).encode('utf-8'))




            
            
            
            while True:
                # Recieve data from client
                data = client_socket.recv(128).decode('utf8').strip()
                if not loggedIn:
                    hash_auth = hashlib.sha256()
                    hash_auth.update((auth_token+key).encode('utf-8'))
                    if not cipher == 'null':
                        padded_data = decryptor.update(data) + decryptor.finalize()
                        data = unpadder.update(padded_data) + unpadder.finalize()
                    # Check user's credintials
                    if hash_auth.hexdigest() == data:
                        loggedIn = True
                        # Prompt user to enter a command
                        client_socket.send(b'Welcome to the back-door server\nEnter your commands:\n')
                    else:
                        # Terminate client socket if wrong password is inputted
                        client_socket.send(b'Wrong password! bye\n')
                        client_socket.close()
                        break
#                else:
#                    # Interpret user info by matching it with one of the definitions in the variable
#                    args = data.split()
#                    if args[0] == "off":
#                        do_off(server,client_socket,args)
#                    elif args[0] == "logout":
#                        do_logout(client_socket,args)
#                        loggedIn = False
#                        break
#                    else:
#                        if not args[0] in interpretInput:
#                            client_socket.send(b'\033[91mNo such command\n\033[0m')
#                        else:
#                            interpretInput[args[0]](client_socket,args)
    except Exception as err:
        print(err)

# close clients socket
client_socket.close()
# close the server socket
server.close()
# terminate the program
sys.exit()




