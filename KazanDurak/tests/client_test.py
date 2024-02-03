import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/home/boulat/PycharmProjects/CardGame')

from KazanDurak.server_client.client import connect_to_server
from KazanDurak.ClientClasses import ClientTextAnimation

server_socket = connect_to_server()
ClientTextAnimation(server_socket)

while True:
    message = input()
    if message.lower() == 'q':
        break
    print('press q to exit')
server_socket.close()
