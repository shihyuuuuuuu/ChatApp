import socket
import sys

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

