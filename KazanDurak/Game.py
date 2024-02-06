from __future__ import annotations
from functools import reduce, wraps
from typing import Callable, Literal

from KazanDurak.TaskManager import task_manager
from KazanDurak.Card import Card
from KazanDurak.Player import Player
from KazanDurak.Container import Container


class GameZoneError(Exception):
    pass


class Game:
    hand_size = 6
    trump_suit = 3

    def __init__(self, players: list[Player], deck: Container):
        self.players: list[Player] = players
        self.attacking_player: Player = players[0]

        self.discard: Container = Container([])
        self.deck: Container = deck

        self.max_cards_to_beat: int = Game.hand_size
        self.last_turn_result: Literal['taken', 'beaten'] | None = None

        self.game_zone: GameZone = \
            GameZone(self.attacking_player, self.defending_player, self.can_beat, self.max_cards_to_beat)


    @property
    def defending_player(self) -> Player:
        if self.attacking_player == self.players[0]:
            return self.players[1]
        return self.players[0]

    def preparation(self):
        self.shuffle_deck()
        for _ in range(Game.hand_size):
            for player in self.players:
                player.take_card()

    @task_manager
    def shuffle_deck(self):
        self.deck.shuffle()

    def get_cards(self):
        for player in [self.attacking_player, self.defending_player]:
            while self.deck.is_empty() is False and len(player.hand) < Game.hand_size:
                player.take_card()

    def can_beat(self, beating: Card, attacking: Card) -> bool:
        if beating.suit == attacking.suit and beating.seniority > attacking.seniority:
            return True
        if beating.suit == Game.trump_suit and attacking.suit != Game.trump_suit:
            return True
        return False


# class AnimatingGame(Game):
#     @game_overriding
#     def shuffle_deck(self):
#
#
#     @game_overriding
#     def player_takes_card(self, acting_player: Player, card: Card):
#         for player in self.players:
#             if player == acting_player:
#                 player.animation.i_take_card(card)
#             else:
#                 player.animation.player_takes_card(acting_player)


class GameZone:
    """Это очень безопасный класс. Он бросает ошибки, если кто-то пытается сделать что-то не то."""

    def __init__(self, attacking_player: Player, defending_player: Player,
                 can_beat: Callable[[Card, Card], bool], max_cards_to_beat):
        self._attacking_player: Player = attacking_player
        self._defending_player: Player = defending_player
        self._attacking_cards: list[Card] = []
        self._beaten_pairs: list[tuple[Card, Card]] = []  # пары вида (побившая, битая) карты
        self._can_beat: Callable[[Card, Card], bool] = self._can_beat_if_card_is_really_attacking(can_beat)
        self._max_cards_to_beat: int = max_cards_to_beat

    def _can_beat_if_card_is_really_attacking(self, can_beat: Callable):
        @wraps(can_beat)
        def real_can_beat(beating: Card, attacking: Card) -> bool:
            return can_beat(beating, attacking) and attacking in self._attacking_cards
        return real_can_beat

    @property
    def all_cards(self):
        return reduce(lambda s, t: s.extend(t), self._beaten_pairs, self._attacking_cards)

    def clear(self) -> list[Card]:
        ret = self.all_cards
        self._beaten_pairs = []
        self._attacking_cards = []
        return ret

    def _is_empty(self):
        return self.all_cards == []

    def _addable_seniority(self) -> set[int]:
        return set([card.seniority for card in self.all_cards])

    def addable_to_attack(self, card: Card) -> bool:
        if self._is_empty() is True:
            return True
        possible_to_add = len(self._beaten_pairs) + len(self._attacking_cards) < \
                          min(self._max_cards_to_beat, len(self._defending_player.hand))
        if card.seniority in self._addable_seniority() and possible_to_add:
            return True
        return False

    def beat(self, beating: Card, attacking: Card):
        if self._can_beat(beating, attacking) is False:
            raise GameZoneError('beat rules error')
        self._attacking_cards.remove(attacking)
        self._beaten_pairs.append((beating, attacking))

    def add_to_attack(self, card: Card):
        if self.addable_to_attack(card) is False:
            raise GameZoneError('attack rules error')
        self._attacking_cards.append(card)

    def is_all_beaten(self):
        return self._attacking_cards == [] and self._beaten_pairs != []
