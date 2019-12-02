import getpass
import pickle
import socket
import sys
import threading
from helper import UserDataObj, MessageObj, createSocket
HOST = 'localhost'
PORT = 5487
YOUR_NAME = None

def user_exist(*data):
    if len(data) == 1:
        s.sendall(pickle.dumps(UserDataObj('check_name', data[0], '')))
        return True if s.recv(4096).decode() == 'T' else False
    elif len(data) == 2:
        s.sendall(pickle.dumps(UserDataObj('check_name_and_pwd', data[0], data[1])))
        return True if s.recv(4096).decode() == 'T' else False

def register_or_signin():
    global YOUR_NAME
    action = None
    
    while action != '1' and action != '2':
        action = input('Register(1) or Sign in(2)? ')
    
    # Register
    if action == '1':
        while True:
            username = input('Input an username: ')
            if user_exist(username):
                print('Username exist.')
                continue
            break
        while True:
            password = getpass.getpass('Set a password: ')
            if getpass.getpass('Please type your password again: ') == password:
                s.sendall(pickle.dumps(UserDataObj('set_name_and_pwd', username, password)))
                s.sendall(pickle.dumps(UserDataObj('OK', username, '')))
                break
        YOUR_NAME = username
    # Sign in
    elif action == '2':
        while True:
            username = input('Input your username: ')
            if user_exist(username):
                break
            print('Username not exist.')
        while True:
            password = getpass.getpass('Input your password: ')
            if user_exist(username, password):
                s.sendall(pickle.dumps(UserDataObj('OK', username, '')))
                break
            print('Wrong password.')
        YOUR_NAME = username

# Covert domain name to ip address and connect to it.
def get_host_and_connect(s):
    try:
        remote_ip = socket.gethostbyname(HOST)
    except socket.gaierror:
        print('Hostname could not be resolved. Exiting...')
        sys.exit()
    print('Ip address of', HOST, 'is', remote_ip)

    try:
        s.connect((remote_ip, PORT))
    except ConnectionRefusedError:
        print('Server is not running...')
        sys.exit()
    
    print('Socket Connected to', HOST ,'on ip', remote_ip, '...')
    register_or_signin()

# A thread for sending messages
def send_msg_thread():
    global YOUR_NAME
    while True:
        message = input("Type your message: ")
        # If you type 'exit', you will recieve it yourself and disconnect from the server.  See 'recv_msg_thread'
        if message == 'exit':
            to_send = pickle.dumps(MessageObj(YOUR_NAME, YOUR_NAME, message))
            s.sendall(to_send)
            break
        target = input("To whom? ")
        to_send = pickle.dumps(MessageObj(YOUR_NAME, target, message))
        try :
            s.sendall(to_send)
        except socket.error:
            print('Send failed')
            sys.exit()

# A thread for recieving messages
def recv_msg_thread():
    while True:
        reply = s.recv(4096)
        recvObj = pickle.loads(reply)
        # If you recieve a 'exit' message from yourself, you will break from the thread.
        if recvObj.message == 'exit' and recvObj.send_name == YOUR_NAME:
            break
        print(recvObj.send_name + ':' + recvObj.message)

# Create two threads for sending and recieving messages
def communication():
    se = threading.Thread(target = send_msg_thread)
    re = threading.Thread(target = recv_msg_thread)
    se.start()
    re.start()

    # Threads will be joined after it's done
    se.join()
    re.join()

s = createSocket()
get_host_and_connect(s)
communication()
s.close()
