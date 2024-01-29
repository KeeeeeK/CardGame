from Game import Game
from GlobalAnimation import GlobalAnimation
from Player import Player
from Container import classic_full_deck
from Animation import MockLocalAnimations

deck = classic_full_deck()
simple_animation = MockLocalAnimations()
players = [Player('Alice', deck, simple_animation), Player('Bob', deck, simple_animation)]
game = Game(players, deck)
game.shuffle_deck()  # УРААААААА!!!
