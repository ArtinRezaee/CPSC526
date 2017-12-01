import socketserver
import socket, threading
import sys
from collections import deque
import time
import string
import random
import select

authorized = False

if __name__ == "__main__":
    # getting the arguments when server is running with no options
    HOST = sys.argv[1]
    srcPort = int(sys.argv[2])
    channel = sys.argv[3]
    secret = sys.argv[4]
    
    while True:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST,srcPort))
        while True:
            id = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
            print(id)
            client.send(('NICK bot'+id).encode('utf-8'))
            try:
                print('in try')
                client.settimeout(10)
                data = client.recv(16).decode('utf-8')
                print ('IRC said:', data)
                if not data == 'ERR_NICKNAMEINUSE':
                    break
            except socket.timeout:
                break

        client.settimeout(None)
        print('out of loop')
        client.send(('USER bot * * :Bot BotMacBotFace').encode('utf-8'))
        print('send complete')
        client.send(('JOIN '+channel).encode('utf-8'));
        print('going to while')
        while True:
            data = client.recv(16).decode('utf-8')
            print("A message from server:", data)
            if not authorized:
                print(data,secret)
                if data == secret:
                    client.send('ok'.encode('utf-8'))
                    print("Authorized controler accessig ...")
                    authorized = True
                else:
                    client.send('denied'.encode('utf-8'))
                    print("Not authorized to control me ...")
                    break
            else:
                print("receive commands to do things")
