import inspect
from functools import wraps
from KazanDurak.Player import Player
from KazanDurak.Animation import Animation
from KazanDurak.TaskManager import task_manager
from KazanDurak.Card import Card
from KazanDurak.Game import Game
from KazanDurak.Rules import Rules


class GlobalAnimation:
    def __init__(self, players: list[Player], player_animations: list[Animation]):
        """player_animations should be ordered with respect to players"""
        self.players: list[Player] = players
        self.animations: list[Animation] = player_animations
        self.player_anim_pairs: list[tuple[Player, Animation]] = list(zip(players, player_animations))

        for method_name, _ in filter(lambda x: str.startswith(x[0], 'sub_to'),
                                     inspect.getmembers(GlobalAnimation, predicate=inspect.isfunction)):
            getattr(self, method_name)()

    def tell_user_about_exception(self, player: Player, exception: Exception):
        print(type(exception).__qualname__)
        self.animations[self.players.index(player)].emergency_message('FUCK YOU GAME BREAKER')

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

    def sub_to_player_took_all(self):
        @task_manager.sub(Rules.all_taken)
        def decorator_to_all_taken(all_taken):
            def real_all_taken(rules: Rules):
                main_player = rules.game.defending_player
                ret = all_taken(rules)
                for player, anim in self.player_anim_pairs:
                    if player == main_player:
                        anim.i_take_all()
                    else:
                        anim.player_takes_all()
                return ret

            return real_all_taken

    def sub_to_all_beaten(self):
        @task_manager.sub(Rules.all_beaten)
        def decorator_to_all_beaten(all_beaten):
            def real_all_beaten(rules: Rules):
                ret = all_beaten(rules)
                for anim in self.animations:
                    anim.game_zone_to_discard()
                return ret

            return real_all_beaten

    def sub_to_just_attack(self):
        @task_manager.sub(Rules.just_attack)
        def decorator_to_just_attack(just_attack):
            def real_just_attack(rules: Rules, main_player: Player, card: Card):
                ret = just_attack(rules, main_player, card)
                for player, anim in self.player_anim_pairs:
                    if player == main_player:
                        anim.i_attack(card)
                    else:
                        anim.player_attacks(player, card)
                return ret

            return real_just_attack

    def sub_to_beat(self):
        @task_manager.sub(Rules.beat)
        def decorator_to_beat(beat):
            def real_beat(rules: Rules, beating: Card, attacking: Card):
                ret = beat(rules, beating, attacking)
                main_player = rules.game.defending_player
                for player, anim in self.player_anim_pairs:
                    if player == main_player:
                        anim.i_beat_card(beating, attacking)
                    else:
                        anim.player_beats_card(player, beating, attacking)
                return ret

            return real_beat
