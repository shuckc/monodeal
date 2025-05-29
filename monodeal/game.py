import random
from .deck import DECK, Card, PropertyCard, PropertyColour, HouseCard, HotelCard, RENTS
from collections import deque
from . import PlayerProto, Action, GameProto
from typing import Sequence


class SkipAction(Action):
    def apply(self, g: GameProto) -> None:
        pass

    def action_count(self) -> int:
        return 1


class PropertySet:
    def __init__(self, colour: PropertyColour):
        self.colour: PropertyColour = colour
        self.properties: list[PropertyCard] = []
        self.hotel_card: HotelCard | None = None
        self.house_card: HouseCard | None = None
        self.rents: Sequence[int] = RENTS[self.colour]

    def is_complete(self) -> bool:
        return len(self.rents) == len(self.properties)

    def get_rent(self) -> int:
        # TODO: hotel + house logic
        base = self.rents[len(self.properties)]
        if self.house_card:
            base = base + 3
        if self.hotel_card:
            base = base + 5
        return base

    def add_property(self, card: PropertyCard) -> None:
        assert self.colour == card.colour
        self.properties.append(card)


class Player(PlayerProto):
    def __init__(self, name: str) -> None:
        self.name = name
        self.hand: list[Card] = []
        self.cash: list[Card] = []
        self.propertysets: dict[PropertyColour, PropertySet] = {}

    def deal_card(self, card: Card) -> None:
        print(f"Player {self.name} recieved {card} into hand {self.hand}")
        self.hand.append(card)

    def get_action(self, game: GameProto, actions_left: int) -> Action:
        actions = self.generate_actions(game, actions_left)
        if len(actions) > 1:
            return actions[0]
        else:
            return SkipAction()

    def generate_actions(self, game: GameProto, actions_left: int) -> list[Action]:
        actions: list[Action] = []
        for c in self.hand:
            actions.extend(c.generate_moves_for(game, self, game.get_opposition(self)))
        return actions

    def has_won(self) -> bool:
        complete_sets = 0
        for ps in self.propertysets.values():
            if ps.is_complete():
                complete_sets += 1

        return complete_sets >= 3

    def get_discard(self) -> Card:
        return self.hand.pop()

    def __repr__(self) -> str:
        return f"Player {self.name}"

    def add_property(self, card: PropertyCard) -> None:
        colour = card.colour
        ps = self.propertysets.get(colour, None)
        if ps is None:
            ps = PropertySet(colour)
            self.propertysets[colour] = ps
        ps.add_property(card)


class Game(GameProto):
    def __init__(
        self, players: list[Player] = [], random: random.Random = random.Random()
    ):
        self.players = players
        self.deck: deque[Card] = deque()
        self.discarded: deque[Card] = deque()
        self.random = random

    def play(self) -> PlayerProto:
        ls = list(DECK)
        self.random.shuffle(ls)
        self.deck.extend(ls)

        # initial setup
        for i in range(2):
            for p in self.players:
                p.deal_card(self.deck.popleft())

        # game loop
        while True:
            for p in self.players:
                print("{p} ")
                p.deal_card(self.deck.popleft())
                p.deal_card(self.deck.popleft())
                actions = 3
                while actions > 0:
                    a = p.get_action(self, actions)
                    actions = actions - a.action_count()
                    # actions apply themselves to game state
                    print(f"{p} does action {a}")
                    a.apply(self)

                if p.has_won():
                    print(f"{p} has won!")
                    return p

                while len(p.hand) > 7:
                    d = p.get_discard()
                    print(f"{p} discarded {d}")
                    self.discarded.append(d)

    def get_opposition(self, player: PlayerProto) -> Sequence[Player]:
        return [p for p in self.players if p != player]


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
