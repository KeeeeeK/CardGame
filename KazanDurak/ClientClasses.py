import inspect
import socket
from typing import Any
from time import sleep
from copy import copy
from queue import SimpleQueue
from threading import Thread
from abc import ABC, abstractmethod

from .Container import classic_full_deck
from socket_helpers import pack_message, unpack_message, CardIndex
from Animation import ANIMATIONS_LIST


ALL_DECK = classic_full_deck()


class ClientTextAnimation:
    def __init__(self, socket_: socket.socket):
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

    @staticmethod
    def animation_from_instructions(method_index, coded_args):
        args = []
        for arg in coded_args:
            if arg[0] == 'c':
                args.append(str(ALL_DECK[int(arg[1:])]))
            elif arg[0] == 'p':
                args.append(arg)  # TODO: надо, чтоб клиент знал свой индекс
        print(method_index, int(method_index), ANIMATIONS_LIST[int(method_index)])
        print(ANIMATIONS_LIST)
        print(f'Playing animation {ANIMATIONS_LIST[int(method_index)]} with args {args}', end=' ... ')
        sleep(0.5)
        print('Done!')

    def act_by_server_message(self, full_message):
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


# TODO: клиент должен ориентироваться на карты, которые указал сервер при знакомстве


class ClientTextAction(Action):
    def __init__(self, socket_: socket.socket):
        self.sending_queue: SimpleQueue[str] = SimpleQueue()
        self.sending_thread = Thread(target=self._sending_to_server, args=(socket_,), daemon=True)
        self.sending_thread.start()

    def _sending_to_server(self, socket_: socket.socket):
        while True:
            message_to_send = self.sending_queue.get()
            socket_.send(pack_message('0', message_to_send))

    def always_get_text_action(self):
        while True:
            action = input()  # TODO
            match action[0]:
                case 'h':
                    print('Help message')
                case 'q':
                    break
                case 't':
                    self.take_all()
                case 'a':
                    self.attack(...)
                case 'b':
                    self.beat(..., ...)
                case 's':
                    self.say_beaten()
                case _:
                    self.unknown_action_warning(action)

    def _send_list(self, lst: list):
        self.sending_queue.put(' '.join(map(str, lst)))

    def take_all(self) -> None:
        self._send_list([ACTION_LIST.index('take_all')])

    def attack(self, card: CardIndex) -> None:
        self._send_list([ACTION_LIST.index('attack'), card])

    def beat(self, beating: CardIndex, attacking: CardIndex) -> None:
        self._send_list([ACTION_LIST.index('beat'), beating, attacking])

    def say_beaten(self):
        self._send_list([ACTION_LIST.index('say_beaten')])

    @staticmethod
    def unknown_action_warning(bad_instruction: str) -> None:
        print(f"I don't know what \"{bad_instruction}\" means.")
