import random
from .deck import DECK, Card, PropertyCard, PropertyColour
from collections import deque


class PropertySet:
    def __init__(self, colour: PropertyColour, card: PropertyCard):
        self.colour: PropertyColour = colour
        self.cards: PropertyCard = []
        self.add(card)

    def add(self, card: PropertyCard):
        self.cards.add(card)


class Action:
    def apply(self, g: "Game") -> None:
        pass

    def action_count(self) -> int:
        return 1


class SkipAction(Action):
    def apply(self, g: "Game") -> None:
        pass


class Player:
    def __init__(self, name: str) -> None:
        self.name = name
        self.hand: list[Card] = []
        self.cash: list[Card] = []
        self.propertysets: list[PropertySet] = []

    def deal_card(self, card: Card):
        print(f"Player {self.name} recieved {card} into hand {self.hand}")
        self.hand.append(card)

    def get_action(self, game: "Game", actions_left: int) -> Action:
        actions = self.generate_actions(game, actions_left)
        if len(actions) > 1:
            return actions[0]
        else:
            return SkipAction()

    def generate_actions(self, game: "Game", actions_left: int) -> list[Action]:
        return []

    def has_won(self) -> bool:
        return False

    def get_discard(self) -> Card:
        return self.hand.pop()

    def __repr__(self) -> str:
        return f"Player {self.name}"


class Game:
    def __init__(
        self, players: list[Player] = [], random: random.Random = random.Random()
    ):
        self.players = players
        self.deck: deque[Card] = deque()
        self.discarded = []
        self.random = random

    def play(self) -> None:
        ls = list(DECK)
        self.random.shuffle(ls)
        self.deck.extend(ls)

        # initial setup
        for i in range(2):
            for p in self.players:
                p.deal_card(self.deck.popleft())

        print(self)

        # game loop
        while True:
            for p in self.players:
                p.deal_card(self.deck.popleft())
                p.deal_card(self.deck.popleft())
                actions = 3
                while actions > 0:
                    a = p.get_action(self, actions)
                    actions = actions - a.action_count()
                    # actions apply themselves to game state
                    a.apply(self)

                if p.has_won():
                    break

                while len(p.hand) > 7:
                    d = p.get_discard()
                    print(f"{p} discarded {d}")
                    self.discarded.append(d)


class ConsolePlayer(Player):
    pass


class RandomPlayer(Player):
    pass


if __name__ == "__main__":
    a: Player = ConsolePlayer("A")
    b: Player = RandomPlayer("B")
    g: Game = Game(players=[a, b])
    winner = g.play()
    print(winner)
