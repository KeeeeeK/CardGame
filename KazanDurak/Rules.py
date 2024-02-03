from collections import namedtuple
from typing import NamedTuple
from enum import StrEnum

from finite_state_machine import StateMachine, transition

from KazanDurak.Game import Game, GameZone, GameZoneError
from KazanDurak.Player import Player
from KazanDurak.Card import Card


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
        pass

    @transition(source=states.attack_and_beat, target=states.inbetween)
    def all_taken(self):
        pass

    @transition(source=states.beaten_confirm, target=states.inbetween)
    def all_beaten(self):
        pass


    @transition(source=states.inbetween, target=states.no_attack_state)
    def get_cards_and_change_roles(self):
        pass

    @transition(source=states.attack_and_beat, target=states.attack_and_beat)
    def attack(self):
        pass

    @transition(source=states.attack_and_beat, target=states.attack_and_beat)
    def beat(self):
        pass

    @transition(source=states.attack_and_beat, target=states.beaten_confirm)
    def mb_all_beaten(self):
        pass


    @transition(source=states.beaten_confirm, target=states.attack_and_beat)
    def more_attack(self):
        pass

    @transition(source=states.inbetween, target=states.final)
    def endgame(self):
        pass

    @transition(source=states.no_attack_state, target=states.attack_and_beat)
    def first_attack(self):
        pass


    # def _main(self):
    #     # на данном этапе предполагается, что игровое поле уже пусто, у всех уже есть необходимое число карт
    #     # смена ролей уже произведена, так что защищающийся и атакующий игроки указаны верным образом
    #     game = self.game
    #     self.game.game_zone = \
    #         GameZone(game.attacking_player, game.defending_player, game.can_beat, game.max_cards_to_beat)
    #     # Есть два выхода - защищающийся скажет, что всё взял или атакующий скажет, что всё бито
    #


if __name__ == '__main__':
    import subprocess
    diagram = subprocess.run(["fsm_draw_state_diagram", "--class", "Rules:Rules"], capture_output=True, text=True)

    print(diagram.stdout)
