import socketserver
import socket, threading
import sys

class MyTCPHandler(socketserver.BaseRequestHandler):
    BUFFER_SIZE = 4096
    threads = []
    s = socket.socket()
#
#    def setup(self):
#        global address
#        add = address
#        global destPort
#        dst = destPort
#        try:
#            print(add)
#            print(dst)
#            self.s.connect((add,dst))
#        except:
#            print("Server is already connected. Continue")
#        print("end of setup")
#
#        c = threading.Thread(target = self.server2Client)
#        self.threads.append(c)
#        print("Starting the thread")
#        c.start()
#
    def client2Server(self):
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
            # Port forwarding server sends received data from client to its server
            self.s.sendall(data)

    def server2Client(self):
        while 1:
            # Port forwarding server waits to receieve something from its server
            dataSrv = self.s.recv(1024).decode("utf-8")
            if dataSrv:
                print("Hello")
                # Port forwarding server sends received data to its client
                self.request.sendall( bytearray( "My server said: " + dataSrv, "utf-8"))
            else:
                break
#
    def handle(self):
        while 1:
            global address
            add = address
            global destPort
            dst = destPort
            try:
#                print(add)
#                print(dst)
                self.s.connect((add,dst))
            except:
                print("Server is already connected. Continue")
#            print("end of setup")

            c = threading.Thread(target = self.server2Client)
            self.threads.append(c)
#            print("Starting the thread")
            c.start()
            t = threading.Thread(target = self.client2Server)
            self.threads.append(t)
            t.start()
            while 1:
                continue



address = ''
destPort = 0
if __name__ == "__main__":
    if(len(sys.argv)<5):
        srcPort = int(sys.argv[1])
        address = sys.argv[2]
        destPort = int(sys.argv[3])
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
