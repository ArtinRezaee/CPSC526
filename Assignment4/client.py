import socket
import os
import random
import string
import hashlib

if __name__ == "__main__":
	if(len(sys.argv) == 6):
		command = sys.argv[1]
		filename = sys.argv[2]
		destination = sys.argv[3]
		cipher = sys.argv[4]
		key = sys.argv[5]

		host, port = destination.split(':')

		client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			connect.connect((host,port))
		except:
		nonce = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))
		client.sendall((cipher + "," + nonce).encode('utf-8'))

		data = client.recv(128).decode('utf-8')
		auth_data = (data + key).encode('utf-8')
		hash_auth = hashlib.sha256()
		hash_auth.update((auth_data))
		client.sendall(hash_auth.hexdigest().encode('utf-8'))
		result = client.recv(128).decode('utf-8')
	else:
