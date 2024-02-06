from __future__ import annotations
from unicards import unicard
import inspect
import socket
from typing import Any, Literal
from time import sleep
from copy import copy, deepcopy
from queue import SimpleQueue
from threading import Thread
from abc import ABC, abstractmethod

from KazanDurak.Container import classic_full_deck
from KazanDurak.socket_helpers import pack_message, unpack_message, CardIndex
from KazanDurak.Animation import ANIMATIONS_LIST


# def all_animations_except(*methods):
#     anims = deepcopy(ANIMATIONS_LIST)
#     for method in methods:
#         anims.remove(method)
#     return anims
# mock_animations = all_animations_except()


class ClientCard:
    _suit_map = {0: 's', 1: 'c', 2: 'd', 3: 'h'}  # 0: пики, 1: крести, 2: буби, 3: черви
    _seniority_map = {i: str(i + 6) for i in range(5)} | {5: 'J', 6: 'Q', 7: 'K', 8: 'A'}

    def __init__(self, suit: int, seniority: int):
        self.suit: int = suit
        self.seniority: int = seniority

    def __repr__(self) -> str:
        return unicard(self._seniority_map[self.seniority] + self._suit_map[self.suit])

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, other: ClientCard):
        return self.suit == other.suit and self.seniority == other.seniority


# TODO: клиент должен ориентироваться на карты, которые указал сервер при знакомстве
class StateContainer:
    def __init__(self):
        self.cards_in_hand: list[ClientCard] = []
        self.attacking_cards: list[ClientCard] = []


def client_full_deck():
    """Должно быть синхронизировано с classic_full_deck. Иначе беды с различным кодированием"""
    ret = []
    for suit in range(4):
        for seniority in range(9):
            ret.append(ClientCard(suit, seniority))
    return ret

ALL_DECK = client_full_deck()


class ClientTextAnimation:
    def __init__(self, socket_: socket.socket, state_container: StateContainer):
        self.state_container: StateContainer = state_container

        self.__socket = socket_
        self.animation_queue: SimpleQueue[str] = SimpleQueue()

        self.listening_thread = Thread(target=self._listen_for_server_messages, args=(socket_,), daemon=True)
        self.listening_thread.start()
        self.animating_thread = Thread(target=self._always_playing_animation, daemon=True)
        self.animating_thread.start()

    def _listen_for_server_messages(self, socket_: socket.socket):
        while True:
            try:
                # keep listening for a message from `socket_` socket
                full_message = unpack_message(socket_.recv(1024))
            except Exception as e:  # TODO: надо отлавливать конкретные ошибки, а не всё подряд
                # most possibly server no longer connected
                print(f'Disconnecting from server because of error: {e}')
                socket_.close()
                self.disconnection_behaviour()
                break
            else:
                self.act_by_server_message(full_message)

    def _always_playing_animation(self):
        while True:
            animation_instructions = self.animation_queue.get().rsplit()
            self.animation_from_instructions(animation_instructions[0], animation_instructions[1:])

    def animation_from_instructions(self, method_index, coded_args):
        method = ANIMATIONS_LIST[int(method_index)]
        args: list[str] = []
        for arg in coded_args:
            if arg[0] == 'c':
                args.append(str(ALL_DECK[int(arg[1:])]))
            elif arg[0] == 'p':
                args.append(['Alice', 'Bob'][int(arg[1:])])  # TODO: надо, чтоб клиент знал свой индекс
        match method:
            case 'game_zone_to_discard':
                self.state_container.attacking_cards = []
            case 'i_take_card':
                self.state_container.cards_in_hand.append(ALL_DECK[int(coded_args[0][1:])])
            case 'player_takes_all':
                self.state_container.attacking_cards = []
            case 'i_take_all':
                self.state_container.attacking_cards = []
            case 'player_beats_card':
                self.state_container.attacking_cards.remove(ALL_DECK[int(coded_args[2][1:])])
            case 'i_beat_card':
                self.state_container.cards_in_hand.remove(ALL_DECK[int(coded_args[1][1:])])
                self.state_container.attacking_cards.remove(ALL_DECK[int(coded_args[1][1:])])
            case 'player_attacks':
                self.state_container.attacking_cards.append(ALL_DECK[int(coded_args[1][1:])])
            case 'i_attack':
                self.state_container.cards_in_hand.remove(ALL_DECK[int(coded_args[0][1:])])
                self.state_container.attacking_cards.append(ALL_DECK[int(coded_args[0][1:])])

        print(f'Playing animation {method} with args {args}', end=' ... ')
        sleep(0.2)
        print('Done!')

    def act_by_server_message(self, full_message: str):
        code, message = full_message[0], full_message[1:]
        match code:
            case '0':  # simple message with animation instructions
                # here we add animation to queue
                self.animation_queue.put(message)
            # case '1':  # this is special message with no animation
            #     # client tries to do something illegal, so we should warn him immediately
            #     self.emergency_message(message)
            case _:
                raise Exception('Unknown server code error')

    def disconnection_behaviour(self):
        print()
        raise Exception("Server dolbach, I won't connect with him anymore")


class Action(ABC):
    """Это класс действий пользователя"""

    @abstractmethod
    def take_all(self):
        pass

    @abstractmethod
    def attack(self, card: CardIndex):
        pass

    @abstractmethod
    def beat(self, beating: CardIndex, attacking: CardIndex):
        pass

    @abstractmethod
    def say_beaten(self):
        pass


ACTION_LIST = [method_name for method_name, _ in inspect.getmembers(Action, predicate=inspect.isfunction)]



class ClientTextAction(Action):
    def __init__(self, socket_: socket.socket, state_container: StateContainer):
        self.state_container: StateContainer = state_container

        self.sending_queue: SimpleQueue[str] = SimpleQueue()
        self.sending_thread = Thread(target=self._sending_to_server, args=(socket_,), daemon=True)
        self.sending_thread.start()

    def _sending_to_server(self, socket_: socket.socket):
        while True:
            message_to_send = self.sending_queue.get()
            socket_.send(pack_message('0', message_to_send))
            sleep(0.1)

    def client_card_encoding(self, card_index: int, mode: Literal['game_zone', 'hand']) -> CardIndex:
        match mode:
            case 'game_zone':
                return ALL_DECK.index(self.state_container.attacking_cards[card_index])
            case 'hand':
                return ALL_DECK.index(self.state_container.cards_in_hand[card_index])

    def always_get_text_action(self):
        # TODO узнать содержимое руки, узнать играемые сейчас карты
        while True:
            action = input()  # TODO click
            try:
                command, args = action[0], action[1:].split(' ')
                match action[0], len(args):
                    case 'h', _:
                        print('Here should be help message. Let\'s hope God will help you!')
                    case 'q', _:
                        break
                    case 't', 0:
                        self.take_all()
                    case 'a', 1:
                        self.attack(self.client_card_encoding(int(args[0]), 'hand'))
                    case 'b', 2:
                        self.beat(self.client_card_encoding(int(args[0]), 'hand'),
                                  self.client_card_encoding(int(args[1]), 'game_zone'))
                    case 's', 0:
                        self.say_beaten()
                    case _:
                        self.unknown_action_warning(action + '   ... No error')
            except ValueError:
                self.unknown_action_warning(action)
                continue

    def _send_list(self, lst: list):
        self.sending_queue.put(' '.join(map(str, lst)))

    def take_all(self) -> None:
        # print('take_all')
        self._send_list([ACTION_LIST.index('take_all')])

    def attack(self, card: CardIndex) -> None:
        # print('attack')
        self._send_list([ACTION_LIST.index('attack'), card])

    def beat(self, beating: CardIndex, attacking: CardIndex) -> None:
        # print('beat')
        self._send_list([ACTION_LIST.index('beat'), beating, attacking])

    def say_beaten(self):
        # print('say_beaten')
        self._send_list([ACTION_LIST.index('say_beaten')])

    @staticmethod
    def unknown_action_warning(bad_instruction: str) -> None:
        print(f"I don't know what \"{bad_instruction}\" means.")
