from functools import wraps
from .Player import Player
from .Animation import Animation
from .TaskManager import task_manager
from .Game import Game

class GlobalAnimation:
    def __init__(self, players: list[Player], player_animations: list[Animation]):
        """player_animations should be ordered with respect to players"""
        self.players: list[Player] = players
        self.animations: list[Animation] = player_animations
        self.player_anim_pairs: list[tuple[Player, Animation]] = list(zip(players, player_animations))

        # for method_name in methods that begin with sub_:
        #     self.method_name()

    def sub_to_shuffle_deck(self):
        @task_manager.sub(Game.shuffle_deck)
        def decorator_to_shuffle_deck(shuffle_deck):
            def real_shuffle_deck(game: Game):
                for animation in self.animations:
                    animation.shuffle_deck()
                return shuffle_deck(game)
            return real_shuffle_deck


    def sub_to_player_takes_card(self):
        @task_manager.sub(Player.take_card)
        def decorator_for_take_card(take_card):
            def real_take_card(main_player: Player):
                card = take_card(main_player)
                for player, anim in self.player_anim_pairs:
                    if player == main_player:
                        anim.i_take_card(card)
                    else:
                        anim.player_takes_card(main_player)
                return card
            return real_take_card

        # for player in self.players:

# v = []
#
# @task_manager.sub(Game.shuffle_deck)
# def decorator_shuffle_deck(func):
#     @wraps(Game.shuffle_deck)
#     def decorated_shuffle_deck(game: Game):
#         for animation in v:
#             animation.shuffle_deck()
#         return func(game)
#     return decorated_shuffle_deck