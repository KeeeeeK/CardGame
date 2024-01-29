from __future__ import annotations

from typing import Sequence
from random import shuffle

from Card import Card


def classic_full_deck() -> Container:
    ret = []
    for suit in range(4):
        for seniority in range(9):
            ret.append(Card(suit, seniority))
    return Container(ret)


class Container:
    def __init__(self, cards: Sequence[Card]):
        self.cards: list[Card] = list(cards)

    def shuffle(self):
        shuffle(self.cards)
        return self

    def add(self, card: Card):
        self.cards.append(card)
        return self

    def pop(self) -> Card | None:
        if self.cards == []:
            return None
        return self.cards.pop()

    def __len__(self):
        return len(self.cards)

    def is_empty(self) -> bool:
        return self.cards == []
