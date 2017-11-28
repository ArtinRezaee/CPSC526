import socketserver
import socket, threading
import sys
from collections import deque
import time
import string

authorized = False

if __name__ == "__main__":
    # getting the arguments when server is running with no options
    HOST = sys.argv[1]
    srcPort = int(sys.argv[2])
    channel = sys.argv[3]
    secret = sys.argv[4]
    
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST,srcPort))

    
    while True:
        data = client.recv(16).decode('utf-8')
        print("A message from server:", data)
        if not authorized:
            if data == secret:
                print("Authorized controler accessig ...")
                authorized = True
            else:
                print("Not authorized to control me ...")
                break
        else:
            print("receive commands to do things")
