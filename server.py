import pickle
import socket
import sys
import threading
from helper import messageObj, createSocket
HOST = 'localhost'  
PORT = 5487 
MAX_CLIENT_NUM = 10
client_data = {}

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
    while True:
        conn, addr = s_obj.accept()
        name = conn.recv(1024).decode()
        print('Connected with ' + addr[0] + ':' + str(addr[1]) + ' Name:' + name)
        client_data[name] = {'sock_obj': conn, 'addr': addr}
        threads.append(threading.Thread(target = on_new_client, args = (conn, addr)))
        threads[-1].start()
        threading.Thread(target = server_command, args = (s_obj,)).start()
    
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

s = createSocket()
socket_bind_listen(s, HOST, PORT, MAX_CLIENT_NUM)
handle_connections(s)
