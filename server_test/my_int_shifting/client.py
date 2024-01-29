import socket
import random
from threading import Thread

from config import *

# server's IP address
# if the server is not on this machine,
# put the private (network) IP address (e.g 192.168.1.2)
SERVER_HOST = "127.0.0.1"

server_socket = socket.socket()
print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
server_socket.connect((SERVER_HOST, SERVER_PORT))
print("[+] Connected.")


def client_do_smth(message):
    print(f'I did smth with message from server: {message}')


def pack_message_to_server(message):
    return ('0' + message).encode()


def listen_for_messages():
    while True:
        message = server_socket.recv(1024).decode()
        if message == '':
            print('server dolbach')
            break
        print("\n" + message)

t = Thread(target=listen_for_messages, daemon=True)
t.start()
while True:
    message = input()
    if message.lower() == 'q':
        break
    server_socket.send(pack_message_to_server(message))
server_socket.close()
