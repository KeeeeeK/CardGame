import inspect
import socket
from typing import Any
from time import sleep
from copy import copy
from queue import SimpleQueue
from threading import Thread
from abc import ABC, abstractmethod

from socket_helpers import pack_message, unpack_message, CardIndex
from KazanDurak.Card import Card
from KazanDurak.Container import classic_full_deck
from KazanDurak.Player import Player
from KazanDurak.ClientClasses import ACTION_LIST


class ServerActionManager:
    def __init__(self, client_sockets: list[socket.socket], cards: list[Card]):
        self.client_sockets = client_sockets
        self.cards = cards

    def is_action_allowed(self, action_instruction: list[int]):
        # должна быть проверка на то, что карта играемая карта в руке, а также действие соответствует очерёдности
        return True  # TODO

    def _cards_from_indexes(self, indexes: list[int]):
        return list(map(lambda index: self.cards[index], indexes))

    def act_by_user_action(self, action_instruction: list[int]):
        # action_instruction должен быть легальным, то есть проверен is_action_allowed
        method_name, args = ACTION_LIST[action_instruction[0]], self._cards_from_indexes(action_instruction[1:])




