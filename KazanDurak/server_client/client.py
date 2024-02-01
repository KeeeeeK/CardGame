from .config import *
import socket
from threading import Thread

SERVER_HOST = "127.0.0.1"


def connect_to_server() -> socket.socket:
    server_socket = socket.socket()
    print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
    server_socket.connect((SERVER_HOST, SERVER_PORT))
    print("[+] Connected.")
    return server_socket
