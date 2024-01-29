import socket
from threading import Thread
from config import *

# server's IP address
SERVER_HOST = "0.0.0.0"


def server_initialization():
    accepting_socket = socket.socket()
    accepting_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # make the port as reusable port
    accepting_socket.bind((SERVER_HOST, SERVER_PORT))  # bind the socket to the address we specified
    accepting_socket.listen(5)
    print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")
    return accepting_socket


def server_do_smth(client_socket, message):
    print(f'I did something with message "{message}" from {str(client_socket)}')


def unpack_client_message(message: bytes) -> str:
    if message == b'':
        raise BrokenPipeError('empty message means no connection')
    return message[1:].decode()



def listen_for_client(client_socket, client_sockets):
    while True:
        try:
            # keep listening for a message from `cs` socket
            message = unpack_client_message(client_socket.recv(1024))
        except Exception as e:
            # client no longer connected
            print(f'disconnecting client because he is loshara: {e}')
            client_sockets.remove(client_socket)
            client_socket.close()
            break
        else:
            server_do_smth(client_socket, message)
            # # iterate over all connected sockets
            # for client_socket in client_sockets:
            #     # and send the message
            #     client_socket.send(('some hui: ' + message).encode())

def accept_new_clients(accepting_socket, client_sockets: set[socket.socket]):
    while True:
        client_socket, client_address = accepting_socket.accept()
        print(f"[+] {client_address} connected.")
        client_sockets.add(client_socket)
        Thread(target=listen_for_client, args=(client_socket, client_sockets), daemon=True).start()


def server_activate(accepting_socket):
    client_sockets: set[socket.socket] = set()
    Thread(target=accept_new_clients, args=(accepting_socket, client_sockets), daemon=True).start()
    while True:
        message_to_myself = input()
        if message_to_myself == 'q':
            break
        else:
            print('Write q to exit')

    accepting_socket.close()
    for cs in client_sockets:
        cs.close()



if __name__ == '__main__':
    server_activate(server_initialization())
