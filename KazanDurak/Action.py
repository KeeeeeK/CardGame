import inspect
import socket
from typing import Any
from time import sleep
from copy import copy
from queue import SimpleQueue
from threading import Thread
from abc import ABC, abstractmethod
from finite_state_machine.exceptions import InvalidStartState

from KazanDurak.socket_helpers import pack_message, unpack_message, CardIndex
from KazanDurak.Card import Card
from KazanDurak.Container import classic_full_deck
from KazanDurak.Player import Player
from KazanDurak.Rules import Rules, NotYourTurn, IllegalMoveCard
from KazanDurak.GlobalAnimation import GlobalAnimation
from KazanDurak.ClientClasses import ACTION_LIST

class UnknownAction(Exception):
    pass


class ServerActionManager:
    def __init__(self, client_sockets: list[socket.socket], rules: Rules, cards: list[Card],
                 global_animation: GlobalAnimation):
        self.client_sockets: list[socket.socket] = client_sockets
        self.rules: Rules = rules
        self.cards: list[Card] = cards
        self.global_animation: GlobalAnimation = global_animation

        self.action_queue: SimpleQueue[tuple[Player, list[int]]] = SimpleQueue()
        self._receiving_action_threads = \
            [Thread(target=self.always_waiting_for_actions_from, args=(rules.game.players[0],), daemon=True),
             Thread(target=self.always_waiting_for_actions_from, args=(rules.game.players[1],), daemon=True)]
        for thread in self._receiving_action_threads:
            thread.start()
        self._acting_thread = Thread(target=self.always_playing_actions, daemon=True)
        self._acting_thread.start()

    @property
    def defending_player(self):
        return self.rules.game.defending_player

    def always_playing_actions(self):
        while True:
            player, action_instruction = self.action_queue.get()
            self.act_by_action(player, action_instruction)


    def always_waiting_for_actions_from(self, player: Player):
        socket_ = self.client_sockets[self.rules.game.players.index(player)]
        while True:
            try:
                # keep listening for a message from `socket_` socket
                full_message = unpack_message(socket_.recv(1024))
            except Exception as e:  # TODO: надо отлавливать конкретные ошибки, а не всё подряд
                # most possibly server no longer connected
                print(f'Disconnecting from client because of error: {e}')
                socket_.close()
                break
            else:
                self.act_by_user_message(player, full_message)

    def act_by_user_message(self, player: Player, full_message: str):
        code, message_str_lst = full_message[0], full_message[1:].split(' ')
        match code:
            case '0':
                self.action_queue.put((player, list(map(int, message_str_lst))))
            case _:
                raise Exception('Unknown client code error')

    def _cards_from_indexes(self, indexes: list[int]):
        return list(map(lambda index: self.cards[index], indexes))

    def tell_user_about_exception(self, player: Player, exception: Exception):
        self.global_animation.tell_user_about_exception(player, exception)

    def act_by_action(self, player: Player, action_instruction: list[int]):
        # action_instruction должен быть легальным, то есть проверен is_action_allowed
        # пока что ожидается, что все аргументы это индексы карт
        method_name, args = ACTION_LIST[action_instruction[0]], self._cards_from_indexes(action_instruction[1:])
        try:
            match method_name, len(args):
                case 'take_all', 0:
                    if player == self.defending_player:
                        self.rules.all_taken()
                    else:
                        raise NotYourTurn()
                case 'attack', 1:
                    print(self.rules.game.game_zone.addable_to_attack(args[0]))
                    self.rules.trying_attack(player, args[0])
                case 'beat', 2:
                    if player != self.defending_player:
                        raise NotYourTurn()
                    self.rules.beat(args[0], args[1])
                case 'say_beaten', 0:
                    # Если игра на двоих, то всё ок
                    if player != self.defending_player:
                        self.rules.all_beaten()
                    else:
                        raise NotYourTurn()
                case _:
                    raise UnknownAction()
        except InvalidStartState as e:
            self.tell_user_about_exception(player, InvalidStartState(e))
        except NotYourTurn as e:
            self.tell_user_about_exception(player, NotYourTurn(e))
        except IllegalMoveCard as e:
            self.tell_user_about_exception(player, IllegalMoveCard(e))
        except UnknownAction as e:
            self.tell_user_about_exception(player, UnknownAction(e))

