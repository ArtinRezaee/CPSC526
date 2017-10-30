import socketserver
import socket, threading
import sys
from collections import deque

totalConnections = 0
currentConnections = 0
serverOutputs = deque()
forwardersReadCounter = 0
forwardersReadFlags = {}

forwardingLock = threading.Lock()
setupLock = threading.Lock()
serverReadLock = threading.Lock()

class MyTCPHandler(socketserver.BaseRequestHandler):
    BUFFER_SIZE = 4096
    threads = []
    s = socket.socket()

    def client2Server(self):
        global s
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
            # if the command option is raw, clean up the input and simply log it on the port forwarding server
            if logs == '-raw':
                lines = clientData.split('\n')
                for line in lines:
                    print("---> "+line.strip())
            elif logs == "-hex":
                hexCounter = 0
                remainingChars = ''
                lines = clientData.split('\n')
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
            # Port forwarding server sends received data from client to its server
            self.s.sendall(data)

    def forward2Client(self):
        global totalConnections
        global currentConnections
        global serverOutputs
        global forwardersReadCounter
        global forwardersReadFlags

        global totalConnectionsLock
        global currentConnectionsLock


        setupLock.acquire()
        currentConnections += 1
        forwarderId = totalConnections
        totalConnections += 1
        forwardersReadFlags[forwarderId] = False
        setupLock.release()

        while 1:
            with serverReadLock:
                if serverOutputs:
                    with forwardingLock:
                        if forwardersReadFlags[forwarderId] == False:
                            if (forwardersReadCounter < (currentConnections - 1)):
                                self.request.sendall( bytearray( "My server said: " + serverOutputs[0], "utf-8"))
                                forwardersReadFlags[forwarderId] = True
                                forwardersReadCounter += 1
                            else:
                                self.request.sendall( bytearray( "My server said: " + serverOutputs[0], "utf-8"))
                                forwardersReadFlags = forwardersReadFlags.fromkeys(forwardersReadFlags, False)
                                forwardersReadCounter = 0
                                serverOutputs.popleft()

        # Port forwarding server sends received data to its client
        

    def server2Client(self):
        global serverOutputs
        while 1:
            # Port forwarding server waits to receieve something from its server
            dataSrv = self.s.recv(1024).decode("utf-8")
            if dataSrv:
                global logOption
                logs = logOption
                if logs == '-raw':
                    lines = dataSrv.split('\n')
                    for line in lines:
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
                with serverReadLock:
                    serverOutputs.append(dataSrv)

            else:
                break

    def handle(self):
        while 1:
            global address
            add = address
            global destPort
            dst = destPort
            try:
                self.s.connect((add,dst))
            except:
                print("Server is already connected. Continue")

            t = threading.Thread(target = self.client2Server)
            self.threads.append(t)
            t.start()
            
            c = threading.Thread(target = self.server2Client)
            self.threads.append(c)
            c.start()
            
            f = threading.Thread(target = self.forward2Client)
            self.threads.append(f)
            f.start()
            
            while 1:
                continue
                # if self.serverOutputs:
                #     if self.forwardersReadFlags[forwarderId] == False:
                #         print(str(self.forwardersReadCounter) + "\t" + str(self.currentConnections - 1))
                #         if (self.forwardersReadCounter < (self.currentConnections - 1)):
                #             self.request.sendall( bytearray( "My server said: " + self.serverOutputs[0], "utf-8"))
                #             self.forwardersReadFlags[forwarderId] = True
                #             self.forwardersReadCounter += 1
                #         else:
                #             print('last forward')
                #             self.request.sendall( bytearray( "My server said: " + self.serverOutputs[0], "utf-8"))
                #             self.forwardersReadFlags.fromkeys(self.forwardersReadFlags, False)
                #             self.forwardersReadCounter = 0
                #             self.serverOutputs.popleft()


address = ''
logOption = ''
destPort = 0

if __name__ == "__main__":
    if(len(sys.argv)<5):
        srcPort = int(sys.argv[1])
        address = sys.argv[2]
        destPort = int(sys.argv[3])
    elif len(sys.argv)<6:
        logOption = sys.argv[1]
        srcPort = int(sys.argv[2])
        address = sys.argv[3]
        destPort = int(sys.argv[4])
    else:
        logOption = sys.argv[1]
        replaceOption = sys.argv[2]
        replace = sys.argv[3]
        replaceWith = sys.argv[4]
        srcPort = int(sys.argv[5])
        address = sys.argv[6]
        destPort = int(sys.argv[7])

    HOST = "localhost"
    server = socketserver.ThreadingTCPServer((HOST, srcPort), MyTCPHandler)

    server.serve_forever()
