import socketserver
import socket, threading
import sys

class MyTCPHandler(socketserver.BaseRequestHandler):
    BUFFER_SIZE = 4096
    threads = []
    s = socket.socket()
    
    def setup(self):
        global address
        add = address
        global destPort
        dst = destPort
        self.s.connect((add,dst))
        t = threading.Thread(target = self.client2Server)
        self.threads.append(t)
        c = threading.Thread(target = self.server2Client)
        self.threads.append(c)
        t.start()
        c.start()

    def client2Server(self):
        while 1:
            data = self.request.recv(self.BUFFER_SIZE)
            if len(data) == self.BUFFER_SIZE:
                while 1:
                    try:  # error means no more data
                        data += self.request.recv(self.BUFFER_SIZE, socket.MSG_DONTWAIT)
                    except:
                        break
                if len(data) == 0:
                    break
            dataClient = data.decode()
            self.s.sendall(dataClient.encode())
                
    def server2Client(self):
        while 1:
            dataSrv = self.s.recv(1024).decode("utf-8")
            self.request.sendall( bytearray( "My server said: " + dataSrv, "utf-8"))
    
#    def handle(self):
##        while 1:
##            print("%s (%s) wrote: %s" % (self.client_address[0],threading.currentThread().getName(), dataClient.strip()))


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
