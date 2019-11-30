import hashlib
import pickle
import pymysql
import socket
import sys
import threading
from helper import UserDataObj, MessageObj, createSocket
HOST = 'localhost'  
PORT = 5487 
MAX_CLIENT_NUM = 10
client_data = {}

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

# Handle the registration or sign in process
def register_or_signin(conn):
    while True:
        userdata = pickle.loads(conn.recv(1024))
        # Check if the username is in the database.
        if userdata.mode == 'check_name':
            sql = """
                SELECT username
                FROM Info_UserData
                WHERE username = '%s'
            """ % (userdata.username)
            cursor.execute(sql)
            results = cursor.fetchall()
            conn.sendall('T'.encode() if len(results) != 0 else 'F'.encode())
        # Check if the (username, password) pair is in the database.
        elif userdata.mode == 'check_name_and_pwd':
            sql = """
                SELECT username
                FROM Info_UserData
                WHERE username = '%s' AND password = '%s'
            """ % (userdata.username, hashlib.sha256(userdata.password.encode()).hexdigest())
            cursor.execute(sql)
            results = cursor.fetchall()
            conn.sendall('T'.encode() if len(results) != 0 else 'F'.encode())
        # Insert new user data into the database.(Registration)
        elif userdata.mode == 'set_name_and_pwd':
            sql = """
                INSERT INTO Info_UserData(username, password)
                VALUES('%s', '%s')
            """ % (userdata.username, hashlib.sha256(userdata.password.encode()).hexdigest())
            try:
                cursor.execute(sql)
                db.commit()
            except pymysql.DatabaseError as e:
                print(e)
                db.rollback()
        # If the user finishes registration or login, it will send 'OK'.
        # Then this method return his(her) username.
        elif userdata.mode == 'OK':
            return userdata.username

# Bind the socket object to specified host/port, and listen at it.
def socket_bind_listen(s_obj, host, port, max_client_num):
    try:
        s_obj.bind((host, port))
    except socket.error as e:
        print(e)
        sys.exit()
    print('Socket bind complete...')
    
    s_obj.listen(max_client_num)
    print('Socket now listening...')

# This method waits for clients to connect, 
# and start a new thread when a new client is connected.
def handle_connections(s_obj):
    threads = []
    threading.Thread(target = server_command, args = (s_obj,)).start()
    while True:
        conn, addr = s_obj.accept()
        name = register_or_signin(conn)
        print('Connected with ' + addr[0] + ':' + str(addr[1]) + ' Name:' + name)
        client_data[name] = {'sock_obj': conn, 'addr': addr}
        threads.append(threading.Thread(target = on_new_client, args = (conn, addr)))
        threads[-1].start()
    
    # Not used now
    for i in threads:
        i.join()

def server_command(s):
    if(input() == 'exit'):
        # Doesn't actually turn of the program
        print('Turning off the server...')

# Call this method whenever a new client thread created.
def on_new_client(clientsocket, addr):
    while True:
        data = clientsocket.recv(1024)
        if not data:
            print('One client disconnect...')
            break
        recv_msg = pickle.loads(data)
        print('From:', recv_msg.send_name, 'To:', recv_msg.recv_name, 'Message:', recv_msg.message)
        if recv_msg.recv_name in client_data:
            client_data[recv_msg.recv_name]['sock_obj'].sendall(data)
        else:
            print('Person not found...')

db, cursor = connect_to_db()
s = createSocket()
socket_bind_listen(s, HOST, PORT, MAX_CLIENT_NUM)
handle_connections(s)
s.close()
db.close()
