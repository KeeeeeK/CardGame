import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/home/boulat/PycharmProjects/CardGame')

from KazanDurak.server_client.client import connect_to_server
from KazanDurak.ClientClasses import ClientTextAnimation, ClientTextAction, StateContainer

state_container = StateContainer()
server_socket = connect_to_server()
anim = ClientTextAnimation(server_socket, state_container)
acting = ClientTextAction(server_socket, state_container)

acting.always_get_text_action()
server_socket.close()
