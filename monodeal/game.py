import random
from collections import deque
from typing import Mapping, MutableSequence, Sequence

from . import (
    Action,
    Card,
    GameProto,
    PlayerProto,
    PropertyCard,
    PropertyColour,
    PropertySetProto,
)
from .actions import SkipAction, generate_actions
from .deck import ALLOWED_BUILDINGS, DECK, RENTS, HotelCard, HouseCard


class PropertySet(PropertySetProto):
    def __init__(self, colour: PropertyColour):
        self.colour: PropertyColour = colour
        self.properties: list[PropertyCard] = []
        self.hotel: HotelCard | None = None
        self.house: HouseCard | None = None
        self.rents: Sequence[int] = RENTS[self.colour]

    def is_complete(self) -> bool:
        return len(self.rents) == len(self.properties)

    def rent_value(self) -> int:
        # TODO: hotel + house logic
        if len(self.properties) == 0:
            return 0
        base = self.rents[len(self.properties) - 1]
        if not self.is_complete():
            return base
        if self.house:
            base = base + 3
        if self.hotel:
            base = base + 5
        return base

    def add_property(self, card: Card) -> None:
        # TODO: no hotel or house on utility or stations

        if isinstance(card, HouseCard):
            assert self.colour in ALLOWED_BUILDINGS
            assert self.house is None
            assert self.is_complete()
            self.house = card
        elif isinstance(card, HotelCard):
            assert self.colour in ALLOWED_BUILDINGS
            assert self.house is not None
            assert self.hotel is None
            assert self.is_complete()
            self.hotel = card
        elif isinstance(card, PropertyCard):
            assert card.colour == self.colour
            self.properties.append(card)
        else:
            raise ValueError(card)

    def __len__(self) -> int:
        return len(self.properties)

    def __repr__(self) -> str:
        return f"PS({self.colour.name},{len(self.properties)}/{len(self.rents)},{','.join(p.property_name for p in self.properties)},{'+House' if self.house else '-'},{'+Hotel' if self.hotel else '-'})"

    def remove(self, card: Card) -> None:
        if isinstance(card, HouseCard):
            assert self.house == card
            self.house = None
        elif isinstance(card, HotelCard):
            assert self.hotel == card
            self.hotel = None
        elif isinstance(card, PropertyCard):
            self.properties.remove(card)
        else:
            raise ValueError(card)

    def cash_value(self) -> int:
        value = sum(card.cash for card in self.properties)
        if self.house:
            value += self.house.cash
        if self.hotel:
            value += self.hotel.cash
        return value

    def __copy__(self) -> "PropertySet":
        c = PropertySet(self.colour)
        for card in self.properties:
            c.add_property(card)
        if self.house:
            c.add_property(self.house)
        if self.hotel:
            c.add_property(self.hotel)
        return c


class Player(PlayerProto):
    def __init__(self, name: str) -> None:
        self.name = name
        self.hand: list[Card] = []
        self.cash: list[Card] = []
        self.propertysets: dict[PropertyColour, PropertySet] = {}

    def deal_card(self, card: Card) -> None:
        print(f"Player {self.name} recieved {card}")
        self.hand.append(card)

    def get_action(self, game: GameProto, actions_left: int) -> Action:
        actions = generate_actions(game, self, actions_left)
        actions.append(SkipAction(self))
        return actions[0]

    def get_hand(self) -> MutableSequence[Card]:
        return self.hand

    def get_property_sets(self) -> Mapping[PropertyColour, PropertySetProto]:
        return self.propertysets

    def get_money_set(self) -> MutableSequence[Card]:
        return self.cash

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

    def add_money(self, card: Card) -> None:
        self.cash.append(card)

    def get_money(self) -> int:
        return sum(card.cash for card in self.cash)

    def get_property_as_cash(self) -> int:
        return sum(ps.cash_value() for ps in self.propertysets.values())

    def choose_how_to_pay(self, amount: int) -> Sequence[Card]:
        # if we have bank funds equal to amount, use that
        total_cash = self.get_money() + self.get_property_as_cash()
        to_pay = min(total_cash, amount)

        # rank options by minimising (ps,rv,excess)
        #   ps - reduction in complete property sets
        #   rv - reduction in rental value
        #   excess - cash sent above to_pay
        # e.g. a spend of [1,3,10] [Green->[G,G,G,H,H], Red->[R]]
        #  for a target to_pay=6 could be [3,R] at (0,2,0)
        #        target to_pay=20 could be [10,3,1,H,H,R] (0,7,1)
        #        target to_pay=22 could be [10,3,1,H,H,R,G] (1,9,0)
        #
        # order of cards does not matter

        # cards: list[Card] = [*self.get_money_set()]
        for ps in self.propertysets.values():
            pass

        for c in self.cash:
            if c.cash == to_pay:
                return [c]
        # if we have one or more totalling, use that
        return []


class Game(GameProto):
    def __init__(
        self, players: list[Player] = [], random: random.Random = random.Random()
    ):
        self.players = players
        self.deck: deque[Card] = deque()
        self.discarded: deque[Card] = deque()
        self.random = random

    def _play(self) -> PlayerProto:
        ls = list(DECK)
        self.random.shuffle(ls)
        self.deck.extend(ls)

        # initial setup
        for i in range(5):
            for p in self.players:
                p.deal_card(self.deck.popleft())

        # game loop
        while True:
            for p in self.players:
                print(f"{p} go")
                p.deal_card(self.deck.popleft())
                p.deal_card(self.deck.popleft())
                print(f"{p} has hand {p.hand}")
                print(f"{p} has property {p.propertysets.values()}")

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

    def play(self) -> PlayerProto:
        try:
            return self._play()
        except:
            print(f"deck: {self.deck}")
            print(f"discarded: {self.discarded}")
            for p in self.players:
                print(p)
                print(f"    hand: {p.hand}")
                print("    property:")
                for v in p.propertysets.values():
                    print(f"      {v}")
                print(f"    cash: {p.cash}")
            raise

    def get_opposition(self, player: PlayerProto) -> Sequence[Player]:
        return [p for p in self.players if p != player]

    def player_owes_money(
        self, from_player: PlayerProto, to_player: PlayerProto, amount: int
    ) -> None:
        cards: Sequence[Card] = from_player.choose_how_to_pay(amount)
        amount_sent = sum(card.cash for card in cards)

        for c in cards:
            try:
                from_player.get_money_set().remove(c)
            except ValueError:
                # must be a property card or property wild card
                if isinstance(c, PropertyCard):
                    from_player.get_property_sets()[c.colour].remove(c)
                else:
                    raise ValueError("not property card?")
        if amount_sent < amount:
            # check player has nothing left if underpaying
            assert len(from_player.get_money_set()) == 0
            for ps in from_player.get_property_sets():
                assert len(ps) == 0

        for c in cards:
            if isinstance(c, PropertyCard):
                to_player.add_property(c)
            else:
                to_player.add_money(c)


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
