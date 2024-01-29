from abc import ABC, abstractmethod
from typing import Sequence

from random import shuffle


class Card(ABC):
    pass


class Container(ABC):
    # Подразумевается, что это конечный контейнер. Бесконечные контейнеры - это совсем другая тема
    @abstractmethod
    def __init__(self, cards: Sequence[Card]):
        self._cards: list[Card] = list(cards)

    @property
    @abstractmethod
    def cards(self) -> list[Card]:
        return self._cards

    @abstractmethod
    def shuffle(self):
        shuffle(self._cards)
        return self

    @abstractmethod
    def add(self, card: Card):
        self.cards.append(card)
        return self

    @abstractmethod
    def pop(self) -> Card:
        return self.cards.pop()
