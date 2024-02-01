from threading import Thread
from queue import SimpleQueue
import socket
from .config import *

# server's IP address
SERVER_HOST = "0.0.0.0"


def _server_initialization() -> socket.socket:
    accepting_socket = socket.socket()
    accepting_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # make the port as reusable port
    accepting_socket.bind((SERVER_HOST, SERVER_PORT))  # bind the socket to the address we specified
    accepting_socket.listen(2)
    print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")
    return accepting_socket


def _accept_new_clients(accepting_socket, client_sockets: set[socket.socket], new_clients: SimpleQueue[socket.socket]):
    while True:
        client_socket, client_address = accepting_socket.accept()
        print(f"[+] {client_address} connected.")
        client_sockets.add(client_socket)
        new_clients.put(client_socket)


def server_activate(new_clients: SimpleQueue[socket.socket]) -> tuple[socket.socket, set[socket.socket]]:
    accepting_socket: socket.socket = _server_initialization()
    client_sockets: set[socket.socket] = set()
    Thread(target=_accept_new_clients, args=(accepting_socket, client_sockets, new_clients), daemon=True).start()
    return accepting_socket, client_sockets

