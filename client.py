import pickle
import socket
import sys
HOST = 'localhost'
PORT = 5487
YOUR_NAME = None

class messageObj():
    def __init__(self, sender, reciever, msg):
        self.send_name = sender
        self.recv_name = reciever
        self.message = msg

def createSocket():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print('Failed to create socket.')
        sys.exit()
    print('Socket created...')
    return s

def getHostAndConnect(s):
    try:
        remote_ip = socket.gethostbyname(HOST)
    except socket.gaierror:
        print('Hostname could not be resolved. Exiting')
        sys.exit()
    print('Ip address of', HOST, 'is', remote_ip)

    s.connect((remote_ip, PORT))
    print('Socket Connected to', HOST ,'on ip', remote_ip, '...')

def communication():
    YOUR_NAME = input("Please input your name: ")
    print("Your name is " + YOUR_NAME + '.')
    while True:
        message = input("Type your message: ")
        target = input("To whom? ")
        to_send = pickle.dumps(messageObj(YOUR_NAME, target, message))
        try :
            s.sendall(to_send)
        except socket.error:
            print('Send failed')
            sys.exit()
        reply = s.recv(4096)
        recvObj = pickle.loads(reply)
        print(recvObj.send_name + ':' + recvObj.message)
        if recvObj.message == 'exit':
            break

s = createSocket()
getHostAndConnect(s)
communication()
s.close()
