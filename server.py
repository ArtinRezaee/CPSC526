import socketserver
import socket, threading
import sys
from collections import deque
import time
import string
import re, binascii

# Global variables to be used by the threads
totalConnections = 0
currentConnections = 0
serverOutputs = deque()
forwardersReadCounter = 0
forwardersReadFlags = {}

# Locks to prevent race conditions
forwardingLock = threading.Lock()
setupLock = threading.Lock()
serverReadLock = threading.Lock()

class MyTCPHandler(socketserver.BaseRequestHandler):
    BUFFER_SIZE = 4096
    # List of reader threads
    threads = []
    # socket that forwarding server connects with to the server
    s = socket.socket()

    # Forwarding server sends info to server
    def client2Server(self):
        global s
        global address
        ad = address
        print("New Connection: ", time.strftime("%Y-%m-%d %H:%M"),", from",ad)
        while 1:
            # Port forwarding server waits to receive something from its client
            data = self.request.recv(self.BUFFER_SIZE)
            if len(data) == self.BUFFER_SIZE:
                while 1:
                    try:  # error means no more data
                        data += self.request.recv(self.BUFFER_SIZE, socket.MSG_DONTWAIT)
                    except:
                        break
                if len(data) == 0:
                    break
            global logOption
            logs = logOption
            # Decode clientData to use for input modification
            clientData = data.decode()
            

            regex = re.compile('-auto\d+')
            match = regex.match(logs)
            # if the command option is raw, clean up the input and simply log it on the port forwarding server
            if logs == '-raw':
                lines = clientData.split('\n')
                for line in lines:
                    print("---> "+line.strip())
        # Strip command. Go through the line and replace non printables with dots
            elif logs == '-strip':
                lines = clientData.split('\n')
                for line in lines:
                    for character in line:
                        if character not in string.printable:
                            line = line.replace(character, ".")
                    print("<--- "+line.strip())

            # if command is hex
            elif logs == "-hex":
                hexCounter = 0
                remainingChars = ''
                # Get each line of data
                lines = clientData.split('\n')
                # for each line of data join characters in the same line together or add a . to the first character on line below and join
                for line in lines:
                    nline = "".join(line.split())
                    if not remainingChars:
                        remainingChars = nline
                    else:
                        remainingChars += '.'+nline
                formattedLine = ''
                chars = ''
                # Go through the characters and print every 16 character and format the hex digits based on very 8th character
                for i in range(0,len(remainingChars)):
                    if (i%16 == 0 and not i == 0):
                        print("---> "+hex(hexCounter)[2:].zfill(8),end='   ')
                        print(formattedLine+'|'+chars+'|')
                        hexCounter += 16
                        formattedLine =''
                        chars=''
                    elif i+1 == len(remainingChars):
                        print("---> "+hex(hexCounter)[2:].zfill(8),end='   ')
                        spaces = 70 - int(len(formattedLine+'|'+chars+'|'))
                        print(formattedLine+' '*spaces+'|'+chars+'|')
                        hexCounter += 16
                        formattedLine =''
                        chars=''
                    if (i+1)%8 == 0:
                        formattedLine += hex(ord(remainingChars[i]))[2:].zfill(2)+'   '
                    else:
                        formattedLine += hex(ord(remainingChars[i]))[2:].zfill(2)+' '
                    chars += remainingChars[i]

            # AutoN command
            elif not match == None:
                lines = clientData
                # Number of bytes to divide to
                num_bytes = int(logs.replace("-auto",""))
                counter = 0
                temp = ""
                # read charactr by character, and determine if characters are ascii or not
                for character in lines:
                    num_value = int(binascii.hexlify(str.encode(character)), 16)
                    if(counter < num_bytes):
                        counter += 1
                        if num_value == 92:
                            temp = temp + "\\\\"
                        elif num_value == 9:
                            temp = temp + "\\t"
                        elif num_value == 10:
                            temp = temp + "\\n"
                        elif num_value == 13:
                            temp = temp + "\\r"
                        elif num_value <= 127 and num_value >= 32:
                            temp = temp + character
                        else:
                            temp = temp + "/" + str(num_value)
                    else:
                        print("<--- " + temp)
                        counter = 1
                        temp = ""
                        if num_value == 92:
                            temp = temp + "\\\\"
                        elif num_value == 9:
                            temp = temp + "\\t"
                        elif num_value == 10:
                            temp = temp + "\\n"
                        elif num_value == 13:
                            temp = temp + "\\r"
                        elif num_value <= 127 and num_value >= 32:
                            temp = temp + character
                        else:
                            temp = temp + "/" + str(num_value)

            # Port forwarding server sends received data from client to its server
            global replaceOption
            replaceOpt = replaceOption
            
            # if there is a replace option, loop through the lines of data, find that word and replace it with new word and send it to the client otherwise send the data as is
            if replaceOpt == '-replace':
                lines = clientData.split('\n')
                replacedData = ''
                for line in lines:
                    if replace in line:
                        line = line.replace(replace,replaceWith)
                        replacedData += line+'\n'
                    else:
                        replacedData += line+'\n'
                self.s.sendall(replacedData.encode())
            else:
                self.s.sendall(data)

#Readed threads that send port forwarding data received from the server to the client to handle multiple connections
    def forward2Client(self):
        global totalConnections
        global currentConnections
        global serverOutputs
        global forwardersReadCounter
        global forwardersReadFlags

        global totalConnectionsLock
        global currentConnectionsLock

        #Acquire the lock to prevent race conditions
        setupLock.acquire()
        # Number of current connections incremented on every thread creation
        currentConnections += 1
        # Id of the forwarder on every thread creation
        forwarderId = totalConnections
        #total connections increamented on every thread connection
        totalConnections += 1
        # set read flag false for the reader
        forwardersReadFlags[forwarderId] = False
        # set up the lock
        setupLock.release()

        while 1:
            with serverReadLock:
                # if there is an output from the server
                if serverOutputs:
                    # if we have the lock
                    with forwardingLock:
                        # if we havent read this message before and we are not the last reader
                        if forwardersReadFlags[forwarderId] == False:
                            if (forwardersReadCounter < (currentConnections - 1)):
                                # send the message to the reader and change the flag and increament the number of read forwarders
                                self.request.sendall( bytearray(serverOutputs[0], "utf-8"))
                                forwardersReadFlags[forwarderId] = True
                                forwardersReadCounter += 1
                            else:
                                # if we are the last reader, send the message and pop the message from queue
                                self.request.sendall( bytearray(serverOutputs[0], "utf-8"))
                                forwardersReadFlags = forwardersReadFlags.fromkeys(forwardersReadFlags, False)
                                forwardersReadCounter = 0
                                serverOutputs.popleft()

    # Port forwarding server sends received data to its client
    # All raw, hex, replace, strip, and autoN commands same as above
    def server2Client(self):
        global serverOutputs
        while 1:
            # Port forwarding server waits to receieve something from its server
            dataSrv = self.s.recv(1024).decode("utf-8")
            if dataSrv:
                global logOption
                logs = logOption
                
                regex = re.compile('-auto\d+')
                match = regex.match(logs)
                if logs == '-raw':
                    lines = dataSrv.split('\n')
                    for line in lines:
                        print("<--- "+line.strip())

                elif logs == '-strip':
                    lines = dataSrv.split('\n')
                    for line in lines:
                        for character in line:
                            if character not in string.printable:
                                line = line.replace(character, ".")
                        print("<--- "+line.strip())

                elif logs == "-hex":
                    hexCounter = 0
                    remainingChars = ''
                    lines = dataSrv.split('\n')
                    for line in lines:
                        nline = "".join(line.split())
                        if not remainingChars:
                            remainingChars = nline
                        else:
                            remainingChars += '.'+nline
                    formattedLine = ''
                    chars = ''
                    for i in range(0,len(remainingChars)):
                        if (i%16 == 0 and not i == 0):
                            print("<--- "+hex(hexCounter)[2:].zfill(8),end='   ')
                            print(formattedLine+'|'+chars+'|')
                            hexCounter += 16
                            formattedLine =''
                            chars=''
                        elif i+1 == len(remainingChars):
                            print("<--- "+hex(hexCounter)[2:].zfill(8),end='   ')
                            spaces = 70 - int(len(formattedLine+'|'+chars+'|'))
                            print(formattedLine+' '*spaces+'|'+chars+'|')
                            hexCounter += 16
                            formattedLine =''
                            chars=''
                        if (i+1)%8 == 0:
                            formattedLine += hex(ord(remainingChars[i]))[2:].zfill(2)+'   '
                        else:
                            formattedLine += hex(ord(remainingChars[i]))[2:].zfill(2)+' '
                        chars += remainingChars[i]

                elif not match == None:
                    lines = dataSrv
                    num_bytes = int(logs.replace("-auto",""))
                    counter = 0
                    temp = ""
                    for character in lines:
                        num_value = int(binascii.hexlify(str.encode(character)), 16)
                        if(counter < num_bytes):
                            counter += 1
                            if num_value == 92:
                                temp = temp + "\\\\"
                            elif num_value == 9:
                                temp = temp + "\\t"
                            elif num_value == 10:
                                temp = temp + "\\n"
                            elif num_value == 13:
                                temp = temp + "\\r"
                            elif num_value <= 127 and num_value >= 32:
                                temp = temp + character
                            else:
                                temp = temp + "/" + str(num_value)
                        else:
                            print("<--- " + temp)
                            counter = 1
                            temp = ""
                            if num_value == 92:
                                temp = temp + "\\\\"
                            elif num_value == 9:
                                temp = temp + "\\t"
                            elif num_value == 10:
                                temp = temp + "\\n"
                            elif num_value == 13:
                                temp = temp + "\\r"
                            elif num_value <= 127 and num_value >= 32:
                                temp = temp + character
                            else:
                                temp = temp + "/" + str(num_value)

                with serverReadLock:
                    global replaceOption
                    replaceOpt = replaceOption
                    if replaceOpt == '-replace':
                        lines = dataSrv.split('\n')
                        replacedData = ''
                        for line in lines:
                            if replace in line:
                                line = line.replace(replace,replaceWith)
                                replacedData += line+'\n'
                            else:
                                replacedData += line+'\n'
                        serverOutputs.append(replacedData)
                    else:
                        serverOutputs.append(dataSrv)
            else:
                break
                    
    # TCP handler
    def handle(self):
        while 1:
            global address
            add = address
            global destPort
            dst = destPort
            # connect to the dstport specified by the user
            try:
                self.s.connect((add,dst))
            except:
                print("Server is already connected. Continue")
            
            # start client thread
            t = threading.Thread(target = self.client2Server)
            self.threads.append(t)
            t.start()
            
            # start writer thread(server thread)
            c = threading.Thread(target = self.server2Client)
            self.threads.append(c)
            c.start()
            
            # start reader thread
            f = threading.Thread(target = self.forward2Client)
            self.threads.append(f)
            f.start()
            
            while 1:
                continue


address = ''
logOption = ''
destPort = 0
replaceOption = ''

if __name__ == "__main__":
    # getting the arguments when server is running with no options
    if(len(sys.argv)<5):
        srcPort = int(sys.argv[1])
        address = sys.argv[2]
        destPort = int(sys.argv[3])
    # server running with only log options
    elif len(sys.argv)<6:
        logOption = sys.argv[1]
        srcPort = int(sys.argv[2])
        address = sys.argv[3]
        destPort = int(sys.argv[4])
    # server running with both log options and replace options
    else:
        logOption = sys.argv[1]
        replaceOption = sys.argv[2]
        replace = sys.argv[3]
        replaceWith = sys.argv[4]
        srcPort = int(sys.argv[5])
        address = sys.argv[6]
        destPort = int(sys.argv[7])

    # Creating a multithreaded server using the specified host and source port
    HOST = "localhost"
    server = socketserver.ThreadingTCPServer((HOST, srcPort), MyTCPHandler)

    server.serve_forever()
