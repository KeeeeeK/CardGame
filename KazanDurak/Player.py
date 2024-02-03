from KazanDurak.Card import Card
from KazanDurak.Container import Container
from KazanDurak.TaskManager import task_manager

class Player:
    def __init__(self, name: str, deck: Container):
        self.name: str = name
        self.hand: Container = Container([])
        self.deck: Container = deck

    @task_manager
    def take_card(self) -> Card | None:
        card = self.deck.pop()
        if card is None:
            return None
        self.hand.add(card)
        return card
