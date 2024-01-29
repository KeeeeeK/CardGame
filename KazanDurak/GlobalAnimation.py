from Player import Player
from SignalManager import signal_manager


class GlobalAnimation:
    def __init__(self, players: list[Player]):
        self.players: list[Player] = players

    @signal_manager.sub('shuffle_deck')
    def shuffle_deck(self):
        for player in self.players:
            player.animation.shuffle_deck()
