import getpass
import hashlib
import pymysql
import pickle
import socket
import sys
import threading
from helper import messageObj, createSocket
HOST = 'localhost'
PORT = 5487
YOUR_NAME = None

def connect_to_db():
    global db, cursor
    try:
        # Connect to database, Username: root, Password: password, DB: ChatApp
        db = pymysql.connect('localhost', 'root', 'password', 'ChatApp')
        cursor = db.cursor(pymysql.cursors.DictCursor)
        print('DB connected...')
    except:
        print('DB connection error')
    return db, cursor

def register_or_signin():
    action = None
    
    while action != '1' and action != '2':
        action = input('Register(1) or Sign in(2)? ')
    
    # Register
    if action == '1':
        while True:
            username = input('Input an username: ')
            sql = """
                SELECT username
                FROM Info_UserData
                WHERE username = '%s'
            """ % (username)
            cursor.execute(sql)
            results = cursor.fetchall()
            if len(results) != 0:
                print('Username exist.')
                continue
            break
        while True:
            password = hashlib.sha256(getpass.getpass('Set a password: ').encode()).hexdigest()
            if hashlib.sha256(getpass.getpass('Please type your password again: ').encode()).hexdigest() == password:
                break
        sql = """
            INSERT INTO Info_UserData(username, password)
            VALUES('%s', '%s')
        """ % (username, password)
        try:
            cursor.execute(sql)
            db.commit()
        except pymysql.DatabaseError as e:
            print(e)
            db.rollback()
        YOUR_NAME = username
    # Sign in
    elif action == '2':
        while True:
            username = input('Input your username: ')
            sql = """
                SELECT username, password
                FROM Info_UserData
                WHERE username = '%s'
            """ % (username)
            cursor.execute(sql)
            results = cursor.fetchall()
            if len(results) != 0:
                break
            print('Username not exist.')
        while True:
            if results[0]['password'] == hashlib.sha256(getpass.getpass('Input your password: ').encode()).hexdigest():
                break
            print('Wrong password.')
        YOUR_NAME = username

# Covert domain name to ip address and connect to it.
def getHostAndConnect(s):
    global YOUR_NAME
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
    #YOUR_NAME = input("Please input your name: ")
    try:
        s.sendall(YOUR_NAME.encode())
    except socket.error:
        print('Greeting failed')
        sys.exit()

# A thread for sending messages
def send_msg_thread():
    global YOUR_NAME
    while True:
        message = input("Type your message: ")
        # If you type 'exit', you will recieve it yourself and disconnect from the server.  See 'recv_msg_thread'
        if message == 'exit':
            to_send = pickle.dumps(messageObj(YOUR_NAME, YOUR_NAME, message))
            s.sendall(to_send)
            break
        target = input("To whom? ")
        to_send = pickle.dumps(messageObj(YOUR_NAME, target, message))
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
    s = threading.Thread(target = send_msg_thread)
    r = threading.Thread(target = recv_msg_thread)
    s.start()
    r.start()

    # Threads will be joined after it's done
    s.join()
    r.join()

db, cursor = connect_to_db()
register_or_signin()
s = createSocket()
getHostAndConnect(s)
communication()
s.close()
db.close()
