from KazanDurak.Game import Game
from KazanDurak.GlobalAnimation import GlobalAnimation
from KazanDurak.Player import Player
from KazanDurak.Container import classic_full_deck
from KazanDurak.Animation import MockLocalAnimations, ServerAnimation
from KazanDurak.TaskManager import task_manager
import socket


deck = classic_full_deck()
simple_animation = MockLocalAnimations()
# anims = [ServerAnimation()]
players = [Player('Alice', deck), Player('Bob', deck)]
game = Game(players, deck)
global_anims = GlobalAnimation(players, [simple_animation, simple_animation])
global_anims.sub_to_shuffle_deck()
global_anims.sub_to_player_takes_card()


game.shuffle_deck()  # УРААААААА!!!
players[0].take_card()
# print(task_manager.subs)

