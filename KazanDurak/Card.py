from __future__ import annotations
from unicards import unicard


class Card:
    # Это просто отображения для того, чтоб str переводил карту в виде пары чисел в удобный для unicard формат
    _suit_map = {0: 's', 1: 'c', 2: 'd', 3: 'h'}  # 0: пики, 1: крести, 2: буби, 3: черви
    _seniority_map = {i: str(i + 6) for i in range(5)} | {5: 'J', 6: 'Q', 7: 'K', 8: 'A'}

    def __init__(self, suit: int, seniority: int):
        self.suit: int = suit
        self.seniority: int = seniority

    def __str__(self) -> str:
        return unicard(self._seniority_map[self.seniority] + self._suit_map[self.suit])


if __name__ == '__main__':
    c = Card(0, 6)
    print(str(c))
