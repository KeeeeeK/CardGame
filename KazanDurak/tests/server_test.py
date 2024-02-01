import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/home/boulat/PycharmProjects/CardGame')

from KazanDurak.Game import Game
from KazanDurak.GlobalAnimation import GlobalAnimation
from KazanDurak.Player import Player
from KazanDurak.Container import classic_full_deck
from KazanDurak.Animation import ServerAnimation, Animation
from KazanDurak.TaskManager import task_manager

import socket
from time import sleep
from queue import SimpleQueue
from KazanDurak.server_client.server import server_activate

new_clients = SimpleQueue()
accepting_socket, client_sockets = server_activate(new_clients)
while new_clients.qsize() < 2:
    sleep(1)
    print(f'...zzz... There {new_clients.qsize()} clients ...zzz...')

# deck_copy = classic_full_deck()
deck = classic_full_deck()
players = [Player('Alice', deck), Player('Bob', deck)]
game = Game(players, deck)


animations: list[Animation] = []
for i in range(2):
    client_socket = new_clients.get()
    animations.append(ServerAnimation(client_socket, players, deck.cards))


global_anims = GlobalAnimation(players, animations)
global_anims.sub_to_shuffle_deck()
global_anims.sub_to_player_takes_card()


# game.shuffle_deck()
players[0].take_card()

while True:
    message_to_myself = input()
    if message_to_myself == 'q':
        break
    else:
        print('Write q to exit')

accepting_socket.close()
for cs in client_sockets:
    cs.close()
