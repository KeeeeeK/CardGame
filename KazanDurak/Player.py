from Card import Card
from Container import Container
from Animation import Animation


class Player:
    def __init__(self, name: str, deck: Container, animation: Animation):
        self.name: str = name
        self.hand: Container = Container([])
        self.deck: Container = deck
        self.animation: Animation = animation

    def take_card(self) -> Card | None:
        card = self.deck.pop()
        if card is None:
            return None
        self.hand.add(card)
        return card
