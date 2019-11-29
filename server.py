import _thread
import pickle
import socket
import sys
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
    while True:
        conn, addr = s_obj.accept()
        print('Connected with ' + addr[0] + ':' + str(addr[1]))
        name = conn.recv(1024).decode()
        client_data[name] = {'sock_obj': conn, 'addr': addr}
        _thread.start_new_thread(on_new_client, (conn, addr))

# Call this method whenever a new client thread created.
def on_new_client(clientsocket, addr):
    while True:
        data = clientsocket.recv(1024)
        recv_msg = pickle.loads(data)
        print('From:', recv_msg.send_name, 'To:', recv_msg.recv_name, 'Message:', recv_msg.message)
        if recv_msg.recv_name in client_data:
            client_data[recv_msg.recv_name]['sock_obj'].sendall(data)
        else:
            print('Person not found...')
        if recv_msg.message == 'exit':
            clientsocket.close()
            break

s = createSocket()
socket_bind_listen(s, HOST, PORT, MAX_CLIENT_NUM)
handle_connections(s)

s.close()
