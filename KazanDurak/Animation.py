import inspect
import socket
from time import sleep
from copy import copy
from queue import SimpleQueue
from threading import Thread
from abc import ABC, abstractmethod

from KazanDurak.socket_helpers import pack_message, unpack_message
from KazanDurak.Card import Card
from KazanDurak.Container import classic_full_deck
from KazanDurak.Player import Player


class Animation(ABC):
    """
    Это абстрактный класс для анимаций одного игрока, от которого должны наследоваться ServerAnimation и ClientAnimation

    ServerAnimation при вызове некоторой анимации должен отправлять клиенту инструкцию по выполнению данной анимации.
    Анимации, от которых ожидается ответ, действительно останавливают основной поток, однако должны иметь опцию выхода.
    По сути, все классы дёргают экземпляры именно этого класса, однако абстрактный класс необходим именно для одинаковых
    методов.

    ClientAnimation должен просто получать инструкции по выполнению анимаций и добавлять их в очередь. По мере обработки
    инструкций из очереди могут отправляться сообщения на сервер.

    # TODO: на самом деле, socket на udp это слишком низкоуровнево. Нужно переходить на что-то типа zmq + json.
    __Протокол связи__:
    _Знакомство_:
    Сервер присылает клиенту его номер: 0 или 1.
    _Дефолтное_общение_:
    Сообщения сервера имеют вид код+содержание. Сообщения с кодом 0 на стороне клиента кладутся в очередь анимаций.

    Содержание это индекс_метода_анимации + последовательность кодированных аргументов.
    Если аргументом является игрок, то он может быть закодирован через p0 или p1.
    Если аргументом является карта, то она кодируется как 'c' + индекс от 0 до количества карт в колоде
    """

    @abstractmethod
    def shuffle_deck(self):
        pass

    @abstractmethod
    def game_zone_to_discard(self):
        pass

    @abstractmethod
    def i_take_card(self, card: Card):
        pass

    @abstractmethod
    def player_takes_card(self, player: Player):
        pass

    @abstractmethod
    def player_takes_all(self):
        pass

    @abstractmethod
    def i_take_all(self):
        pass

    @abstractmethod
    def player_beats_card(self):
        pass

    @abstractmethod
    def i_beat_card(self):
        pass

    @abstractmethod
    def player_attacks(self):
        pass

    @abstractmethod
    def i_attack(self):
        pass

    @abstractmethod
    def emergency_message(self):
        pass


ANIMATIONS_LIST = [method_name for method_name, _ in inspect.getmembers(Animation, predicate=inspect.isfunction)]

ALL_DECK = classic_full_deck().cards


def _func_generator(method_name):
    def func(*args):
        print(f'Server asked to play animation {method_name} with args {args[1:]}')

    return func


def SimpleTextAnimationsReplacement(cls):
    abs_methods = cls.__abstractmethods__
    delattr(cls, '__abstractmethods__')
    for method in abs_methods:
        setattr(cls, method, _func_generator(method))
    return cls


@SimpleTextAnimationsReplacement
class MockLocalAnimations(Animation):
    pass



class ServerAnimation(Animation):
    def __init__(self, socket_: socket.socket, players: list[Player], cards: list[Card]):
        self.sending_queue: SimpleQueue[str] = SimpleQueue()
        self.sending_thread = Thread(target=self._sending_to_client, args=(socket_,), daemon=True)
        self.sending_thread.start()

        self.players = players
        self.cards = copy(cards)

    @classmethod
    def replace_abstract_methods(cls):
        abs_methods = ANIMATIONS_LIST
        delattr(cls, '__abstractmethods__')
        for instruction_index, method_name in enumerate(abs_methods):
            setattr(cls, method_name, cls._instruction_encode_and_put_generator(instruction_index))
        return cls

    @staticmethod
    def _instruction_encode_and_put_generator(instruction_index: int):
        def instruction_encode_and_put(self: ServerAnimation, *args):
            args_indexes: list[str] = [str(instruction_index)]
            for arg in args:
                if isinstance(arg, Player):
                    args_indexes.append(f'p{self.players.index(arg)}')
                elif isinstance(arg, Card):
                    args_indexes.append(f'c{self.cards.index(arg)}')
            self.sending_queue.put(' '.join(args_indexes))

        return instruction_encode_and_put

    def _sending_to_client(self, socket_: socket.socket):
        while True:
            message_to_send = self.sending_queue.get()
            socket_.send(pack_message('0', message_to_send))


ServerAnimation.replace_abstract_methods()
