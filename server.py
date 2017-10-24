import socketserver
import socket, threading
import sys


class MyTCPHandler(socketserver.BaseRequestHandler):
    BUFFER_SIZE = 4096
    def handle(self):
        global address
        add = address
        global destPort
        dst = destPort
        s = socket.socket()
        s.connect((add,dst))
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
            dataClient = data.decode( "utf-8")
            dataSrv = s.recv(1024).decode("utf-8")
            # sending to our client which we are the server to
            self.request.sendall( bytearray( "My server said: " + dataSrv, "utf-8"))
            # sending to our server which we are the client to
            s.sendall(dataClient.encode())
            print("%s (%s) wrote: %s" % (self.client_address[0],threading.currentThread().getName(), dataClient.strip()))


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
