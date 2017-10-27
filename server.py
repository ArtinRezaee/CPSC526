import socketserver
import socket, threading
import sys
from collections import deque

class MyTCPHandler(socketserver.BaseRequestHandler):
    BUFFER_SIZE = 4096
    threads = []
    s = socket.socket()

    serverOutputs = deque()

    totalConnections = 0
    currentConnections = 0
    forwardersReadCounter = 0

    forwardersReadFlags = {}


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
            clientData = data.decode()
            if logs == '-raw':
                lines = clientData.split('\n')
                for line in lines:
                    print("---> "+line.strip())
            # Port forwarding server sends received data from client to its server
            self.s.sendall(data)

    #def forward2Client(self):
        # self.currentConnections += 1
        # forwarderId = self.totalConnections
        # self.totalConnections += 1
        # self.forwardersReadFlags[forwarderId] = False

        # while 1:
        #     if not serverData.empty():
        #         if self.forwardersReadFlags[forwarderId] == False:
        #             if (self.forwardersReadCounter < self.currentConnections):
        #                 self.request.sendall( bytearray( "My server said: " + self.serverOutputs[0], "utf-8"))
        #                 self.forwardersReadFlags[forwarderId] = True
        #                 self.forwardersReadCounter += 1
        #             else:
        #                 self.request.sendall( bytearray( "My server said: " + self.serverOutputs[0], "utf-8"))
        #                 for forwarderId in self.forwardersReadFlags:
        #                     forwarderReadFlags[forwarderId] = False
        #                 self.forwardersReadCounter = 0
        #                 self.serverOutputs.popleft()

        # Port forwarding server sends received data to its client
        

    def server2Client(self):
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
                print(3)
                self.serverOutputs.append(dataSrv)
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
            
            self.currentConnections += 1
            forwarderId = self.totalConnections
            self.totalConnections += 1
            self.forwardersReadFlags[forwarderId] = False

            t = threading.Thread(target = self.client2Server)
            self.threads.append(t)
            t.start()

            while 1:
                if self.serverOutputs:
                    if self.forwardersReadFlags[forwarderId] == False:
                        if (self.forwardersReadCounter < self.currentConnections):
                            self.request.sendall( bytearray( "My server said: " + self.serverOutputs[0], "utf-8"))
                            self.forwardersReadFlags[forwarderId] = True
                            self.forwardersReadCounter += 1
                        else:
                            self.request.sendall( bytearray( "My server said: " + self.serverOutputs[0], "utf-8"))
                            for forwarderId in self.forwardersReadFlags:
                                forwarderReadFlags[forwarderId] = False
                            self.forwardersReadCounter = 0
                            self.serverOutputs.popleft()


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
