from Game import Game
from GlobalAnimation import GlobalAnimation
from Player import Player
from Container import classic_full_deck
from Animation import MockLocalAnimations
from TaskManager import task_manager

deck = classic_full_deck()
simple_animation = MockLocalAnimations()
players = [Player('Alice', deck), Player('Bob', deck)]
game = Game(players, deck)
global_anims = GlobalAnimation(players, [simple_animation, simple_animation])
global_anims.sub_to_shuffle_deck()
global_anims.sub_to_player_takes_card()


game.shuffle_deck()  # УРААААААА!!!
players[0].take_card()
# print(task_manager.subs)

