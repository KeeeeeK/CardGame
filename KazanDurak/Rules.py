from collections import namedtuple
from typing import NamedTuple, LiteralString, Literal
from enum import StrEnum

from finite_state_machine import StateMachine, transition

from KazanDurak.TaskManager import task_manager
from KazanDurak.Game import Game, GameZone, GameZoneError
from KazanDurak.Player import Player
from KazanDurak.Card import Card


class IllegalMoveCard(Exception):
    pass


class NotYourTurn(Exception):
    pass


class states:
    # этот костыль существует, чтоб работало автодополнение и нельзя было ошибиться в названиях
    __slots__ = ['preparation', 'no_attack_state', 'attack_and_beat', 'beaten_confirm', 'inbetween', 'final']


for state in states.__slots__:
    # а этот костыль существует, чтоб диаграмма FSM была читаемой и названия состояний были читаемыми
    setattr(states, state, state)


class Rules(StateMachine):
    # правило расширения класса - расширить пространство states, и только потом расширять его новыми transition-ами
    def __init__(self, game: Game):
        self.state = states.preparation
        super().__init__()
        self.game: Game = game

    @transition(source=states.preparation, target=states.no_attack_state)
    def begin_game(self):
        self.game.preparation()

    @task_manager
    @transition(source=states.attack_and_beat, target=states.inbetween)
    def all_taken(self):
        self.game.defending_player.hand.extend(self.game.game_zone.clear())
        self.game.last_turn_result = 'taken'

    @task_manager
    @transition(source=states.beaten_confirm, target=states.inbetween)
    def all_beaten(self):
        # на данном этапе self.game.game_zone._attacking_cards == []
        self.game.discard.extend(self.game.game_zone.clear())
        self.game.last_turn_result = 'beaten'

    @transition(source=states.inbetween, target=states.no_attack_state)
    def get_cards_and_change_roles(self, last_result: Literal['taken', 'beaten']):
        self.game.get_cards()
        self.change_roles(last_result)

    def change_roles(self, last_result: Literal['taken', 'beaten']):
        match last_result:
            case 'taken':
                # Если игра не вдвоём, то должна быть смена ролей
                pass
            case 'beaten':
                self.game.attacking_player = self.game.defending_player

    @task_manager
    def just_attack(self, player: Player, card: Card):
        # на данном этапе player == self.game.defending_player, а self.game.game_zone.addable_to_attack(card) == True
        if player == self.game.defending_player:
            raise NotYourTurn
        if card not in player.hand:
            raise IllegalMoveCard()
        player.hand.remove(card)
        try:
            self.game.game_zone.add_to_attack(card)
        except GameZoneError as e:
            raise IllegalMoveCard(e)

    @transition(source=states.attack_and_beat, target=states.attack_and_beat)
    def attack(self, player: Player, card: Card):
        self.just_attack(player, card)

    @task_manager
    @transition(source=states.attack_and_beat, target=states.attack_and_beat)
    def beat(self, beating: Card, attacking: Card) -> None:
        try:
            self.game.game_zone.beat(beating, attacking)
        except GameZoneError as e:
            raise IllegalMoveCard(e)
        if self.game.game_zone.is_all_beaten():
            self.mb_all_beaten()

    @transition(source=states.attack_and_beat, target=states.beaten_confirm)
    def mb_all_beaten(self):
        pass

    @transition(source=states.beaten_confirm, target=states.attack_and_beat)
    def gypsy_attack(self, player: Player, card: Card):
        self.just_attack(player, card)

    @transition(source=states.inbetween, target=states.final)
    def endgame(self):
        pass

    @transition(source=states.no_attack_state, target=states.attack_and_beat)
    def first_attack(self, card: Card):
        self.just_attack(self.game.attacking_player, card)

    def trying_attack(self, player: Player, card: Card):
        """Это безопасная функция в том смысле, что она бросает ошибки типа NotYourTurn и IllegalMoveCard"""
        match self.state:
            case states.attack_and_beat:
                self.attack(player, card)
            case states.no_attack_state:
                if self.game.attacking_player != player:
                    raise NotYourTurn
                self.first_attack(card)
            case states.beaten_confirm:
                self.gypsy_attack(player, card)
            case _:
                raise NotYourTurn


if __name__ == '__main__':
    # import subprocess
    #
    # diagram = subprocess.run(["fsm_draw_state_diagram", "--class", "Rules:Rules"], capture_output=True, text=True)
    #
    # print(diagram.stdout)
    from finite_state_machine.exceptions import InvalidStartState

    print(type(Exception))
