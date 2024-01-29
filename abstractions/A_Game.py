from abc import ABC, abstractmethod

class Player(ABC):
    @abstractmethod
    def __init__(self):
        pass

class Game(ABC):
    @abstractmethod
    def __init__(self, players: list[Player]):
        self.players: list[Player] = players
        pass

