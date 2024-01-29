import inspect
import socket
from typing import Any
from time import sleep
from queue import SimpleQueue
from threading import Thread
from abc import ABC, abstractmethod

from Card import Card
from Container import classic_full_deck
# from Player import Player
Player = Any


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



def _unpack_message(full_message: bytes) -> str:
    if full_message == b'':
        raise BrokenPipeError('empty message means no connection')
    return full_message.decode()


def _pack_message(code: chr, message: str) -> bytes:
    return (code + message).encode()


def _func_generator(method_name):
    def func(self, *args):
        print(f'Server asked to play animation {method_name} with args {args[1:]}')
    return func

def SimpleTextAnimationsReplacement(cls):
    abs_methods = cls.__abstractmethods__
    delattr(cls, '__abstractmethods__')
    for method in abs_methods:
        setattr(cls, method, _func_generator(method))
    return cls


# MockLocalAnimations = SimpleTextAnimationsReplacement(Animation)
@SimpleTextAnimationsReplacement
class MockLocalAnimations(Animation):
    def shuffle_deck(self):
        print('shuffle_deck')


class ClientTextAnimation:
    def __init__(self, socket_: socket.socket):
        self.animation_queue: SimpleQueue[str] = SimpleQueue()
        self.sending_queue: SimpleQueue[str] = SimpleQueue()
        self.listening_thread = Thread(target=self._listen_for_server_messages, args=(socket_,), daemon=True)
        self.listening_thread.start()
        self.animating_thread = Thread(target=self._always_playing_animation, daemon=True)
        self.animating_thread.start()
        self.sending_thread = Thread(target=self._sending_to_server, args=(socket_,), daemon=True)
        self.sending_thread.start()


    def _listen_for_server_messages(self, socket_: socket.socket):
        while True:
            try:
                # keep listening for a message from `socket_` socket
                full_message = _unpack_message(socket_.recv(1024))
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

    def _sending_to_server(self, socket_: socket.socket):
        while True:
            message_to_send = self.sending_queue.get()
            socket_.send(_pack_message('0', message_to_send))

    @staticmethod
    def animation_from_instructions(method_index, coded_args):
        args = []
        for arg in coded_args:
            if arg[0] == 'c':
                args.append(str(ALL_DECK[int(arg[1:])]))
            else:
                args.append(arg)
        print(f'Playing animation {ANIMATIONS_LIST[method_index]} with args {args}', end=' ... ')
        sleep(0.7)
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
        print("Server dolbach, I won't connect with him anymore")


class ServerAnimation(Animation):
    def __init__(self, socket_: socket.socket):
        ...

    def send_to_client(self, method, args):
        ...

    # def pack
    # def _managing_client(self, socket_: socket.socket):
    #     while True:
    #         socket_.send(self._pack_message(code, message=))

# c = ClientTextAnimation()
# c.player_beats_card()

if __name__ == '__main__':
    anim = MockLocalAnimations()
    anim.shuffle_deck()