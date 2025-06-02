import copy
import random
from collections import deque
from itertools import chain, combinations
from typing import Iterable, Mapping, MutableSequence, Self, Sequence, Tuple

from . import (
    Action,
    Card,
    GameProto,
    HotelCard,
    HouseCard,
    PlayerProto,
    PropertyCard,
    PropertyColour,
    PropertySetProto,
    WildPropertyCard,
)
from .actions import SkipAction, generate_actions
from .deck import ALLOWED_BUILDINGS, DECK, RENTS


class PropertySet(PropertySetProto):
    def __init__(self, colour: PropertyColour):
        self.colour: PropertyColour = colour
        self.properties: list[PropertyCard] = []
        self.wilds: list[WildPropertyCard] = []
        self.hotel: HotelCard | None = None
        self.house: HouseCard | None = None
        self.rents: Sequence[int] = RENTS[self.colour]

    def is_complete(self) -> bool:
        return len(self.rents) <= len(self.properties) + len(self.wilds)

    def get_colour(self) -> PropertyColour:
        return self.colour

    def rent_value(self) -> int:
        # TODO: hotel + house logic
        card_count = len(self.properties) + len(self.wilds)
        if card_count == 0:
            return 0
        base = self.rents[min(card_count, len(self.rents)) - 1]
        if not self.is_complete():
            return base
        if self.house:
            base = base + 3
        if self.hotel:
            base = base + 5
        return base

    def add_property(self, card: Card) -> Self:
        # TODO: no hotel or house on utility or stations

        if isinstance(card, HouseCard):
            assert self.colour in ALLOWED_BUILDINGS
            assert self.is_complete()
            assert self.house is None
            self.house = card
        elif isinstance(card, HotelCard):
            assert self.colour in ALLOWED_BUILDINGS
            assert self.is_complete()
            assert self.house is not None
            assert self.hotel is None
            self.hotel = card
        elif isinstance(card, PropertyCard):
            assert card.colour == self.colour
            self.properties.append(card)
        elif isinstance(card, WildPropertyCard):
            assert self.colour in card.colours
            self.wilds.append(card)
        else:
            raise ValueError(card)
        return self

    def __len__(self) -> int:
        return (
            len(self.properties)
            + len(self.wilds)
            + (1 if self.house else 0)
            + (1 if self.hotel else 0)
        )

    def __repr__(self) -> str:
        return f"PS({self.colour.name},{len(self.properties)}/{len(self.rents)},{','.join(p.property_name for p in self.properties)},{','.join(p.name for p in self.wilds)},{'+House' if self.house else '-'},{'+Hotel' if self.hotel else '-'})"

    def remove(self, card: Card) -> None:
        if isinstance(card, HouseCard):
            assert self.house == card
            self.house = None
        elif isinstance(card, HotelCard):
            assert self.hotel == card
            self.hotel = None
        elif isinstance(card, PropertyCard):
            self.properties.remove(card)
        elif isinstance(card, WildPropertyCard):
            self.wilds.remove(card)
        else:
            raise ValueError(card)

    def cash_value(self) -> int:
        value = sum(card.cash for card in self.properties)
        value += sum(card.cash for card in self.wilds)
        if self.house:
            value += self.house.cash
        if self.hotel:
            value += self.hotel.cash
        return value

    def __copy__(self) -> "PropertySet":
        c = PropertySet(self.colour)
        for card in self.properties:
            c.properties.append(card)
        for wc in self.wilds:
            c.wilds.append(wc)
        c.house = self.house
        c.hotel = self.hotel
        return c

    def can_build_house(self) -> bool:
        return (
            self.is_complete()
            and self.colour in ALLOWED_BUILDINGS
            and self.house is None
        )

    def can_build_hotel(self) -> bool:
        return (
            self.is_complete()
            and self.colour in ALLOWED_BUILDINGS
            and self.house is not None
            and self.hotel is None
        )


def cash_value(cards: Sequence[Card]) -> int:
    return sum(card.cash for card in cards)


def smallest_cash_remaining_without(
    cards: Sequence[Card], without: Sequence[Card]
) -> int:
    remain = set(cards)
    for w in without:
        remain.remove(w)
    if len(remain) == 0:
        return 9999
    return min(card.cash for card in remain)


def card_powerset(card: Sequence[Card]) -> Iterable[Sequence[Card]]:
    "Subsequences of the iterable from shortest to longest."
    # powerset([1,2,3]) → () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    s = list(card)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


class Player(PlayerProto):
    def __init__(self, name: str) -> None:
        self.name = name
        self.hand: list[Card] = []
        self.cash: list[Card] = []
        self.propertysets: dict[PropertyColour, PropertySet] = {}
        self.cards_to_ps: dict[Card, PropertySet] = {}

    def deal_card(self, card: Card) -> None:
        print(f"Player {self.name} recieved {card}")
        self.hand.append(card)

    def get_action(self, game: GameProto, actions_left: int) -> Action:
        actions = generate_actions(game, self, actions_left)
        actions.append(SkipAction(self))
        print(f"{self} considering {len(actions)} actions")
        return actions[0]

    def get_hand(self) -> MutableSequence[Card]:
        return self.hand

    def get_property_sets(self) -> Mapping[PropertyColour, PropertySetProto]:
        return self.propertysets

    def get_complete_sets_rv(self) -> Tuple[int, int]:
        complete_sets = 0
        rent_value = 0
        for ps in self.propertysets.values():
            if ps.is_complete():
                complete_sets += 1
            rent_value += ps.rent_value()

        return complete_sets, rent_value

    def get_money_set(self) -> MutableSequence[Card]:
        return self.cash

    def has_won(self) -> bool:
        complete_sets, _ = self.get_complete_sets_rv()
        return complete_sets >= 3

    def get_discard(self) -> Card:
        return self.hand.pop()

    def __repr__(self) -> str:
        return f"Player {self.name}"

    def _get_or_create_ps(self, colour: PropertyColour) -> PropertySet:
        ps = self.propertysets.get(colour, None)
        if ps is None:
            ps = PropertySet(colour)
            self.propertysets[colour] = ps
        return ps

    def add_property(
        self,
        colour: PropertyColour,
        card: PropertyCard | WildPropertyCard | HouseCard | HotelCard,
    ) -> None:
        ps = self._get_or_create_ps(colour)
        ps.add_property(card)
        self.cards_to_ps[card] = ps

    def add_money(self, card: Card) -> None:
        self.cash.append(card)

    def remove(self, card: Card) -> None:
        ps: PropertySet | None = self.cards_to_ps.get(card, None)
        if ps:
            ps.remove(card)
            self.cards_to_ps.pop(card)
        else:
            self.cash.remove(card)

    def get_money(self) -> int:
        return cash_value(self.cash)

    def get_property_as_cash(self) -> int:
        return sum(ps.cash_value() for ps in self.propertysets.values())

    def choose_how_to_pay(self, amount: int) -> Sequence[Card]:
        # if we have bank funds equal to amount, use that
        total_cash = self.get_money()
        total_property = self.get_property_as_cash()
        to_pay = min(total_cash + total_property, amount)
        print(
            f"{self} choose_how_to_pay amount={amount} to_pay={to_pay} from {self.cash} and {','.join(str(x) for x in self.cards_to_ps.keys())}"
        )
        best: Sequence[Card] = []
        cards = list(self.cash)
        # includes_property = False

        # if we can pay this amount without dipping into property, do so
        # since it makes the powerset much smaller
        if to_pay > total_cash:
            for c in self.cards_to_ps.keys():
                if isinstance(c, WildPropertyCard) and c.colours == PropertyColour.ALL:
                    continue
                cards.append(c)
        #    includes_property = True

        # iterate over the powerset evaluating a metric for each
        # solution with an overpay >= 0
        #
        # rank options by minimising (ps,rv,sr,overpay)
        #   ps - reduction in complete property sets
        #   rv - reduction in rental value
        #   sr - smallest remaining cash card (as above)
        #   overpay - cash sent above to_pay
        # e.g. a spend of [1,3,10] [Green->[G,G,G,H,H], Red->[R]]
        #  for a target to_pay=6 could be [3,R] at (0,2,0)
        #        target to_pay=20 could be [10,3,1,H,H,R] (0,7,1)
        #        target to_pay=22 could be [10,3,1,H,H,R,G] (1,9,0)
        #
        # order of cards does not matter

        sr_orig = smallest_cash_remaining_without(cards, [])
        ps_orig, rv_orig = self.get_complete_sets_rv()

        least_score = (9999, 0, 0, 0)

        for cs in card_powerset(cards):
            cv = cash_value(cs)
            overpay = cv - to_pay
            if overpay < 0:
                continue

            print(
                f"{self} checking {cs} with cv={cv} overpayment={overpay} [least {least_score}]"
            )
            cs_props = [c for c in cs if c in self.cards_to_ps]
            cs_cash = [c for c in cs if c not in self.cards_to_ps]

            # calculate ps, rv, sr
            ps = 0
            rv = 0
            sr = 0
            score = (ps, rv, overpay, sr)

            if score <= least_score:
                print(" ** improves least_overpayment")

                # OK candidate
                sr = smallest_cash_remaining_without(self.cash, cs_cash)
                score = (ps, rv, overpay, sr)

                if score <= least_score:
                    best = cs
                    least_score = score
                    # exit early if optimal
                    if overpay == 0 and sr == sr_orig:
                        break
        print(
            f"{self} choose_how_to_pay() solver for {amount} (to_pay={to_pay}) chose {best} with ps,rv,overpay,sr={least_score}"
        )
        return list(best)

    def pick_colour_for_recieved_wildcard(
        self, card: WildPropertyCard
    ) -> PropertyColour:
        # maxmimise increase in rv
        best: PropertyColour | None = None
        rv_incr = 0
        for pc in card.colours:
            if best is None:
                best = pc
            ps = self._get_or_create_ps(pc)
            rv_base = ps.rent_value()
            rv_new = copy.copy(ps).add_property(card).rent_value()
            print(
                f"{self} recieved {card} scoring {pc} takes rv from {rv_base} to {rv_new}"
            )
            if rv_new - rv_base > rv_incr:
                rv_incr = rv_new - rv_base
                best = pc
        print(f"{self} chose {card} as {best} with rv_incr {rv_incr}")
        if best is None:
            raise ValueError(f"unable to choose property colour for {card}")
        return best


class Game(GameProto):
    def __init__(
        self, players: list[Player] = [], random: random.Random = random.Random()
    ):
        self.players = players
        self.deck: deque[Card] = deque()
        self.discarded: deque[Card] = deque()
        self.random = random

    def deal_to(self, p: PlayerProto) -> None:
        if len(self.deck) == 0:
            print(f"reshuffling {len(self.discarded)} dicarded cards")
            self.deck.extend(self.discarded)
            self.random.shuffle(self.deck)
            self.discarded.clear()
        p.deal_card(self.deck.popleft())

    def _play(self) -> PlayerProto:
        ls = list(DECK)
        self.random.shuffle(ls)
        self.deck.extend(ls)

        # initial setup
        for i in range(5):
            for p in self.players:
                self.deal_to(p)

        # game loop
        while True:
            for p in self.players:
                print(f"{p} go")
                deal = 5 if len(p.get_hand()) == 0 else 2
                for i in range(deal):
                    self.deal_to(p)
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
            print("==== CRASHED - state was ====")
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
            from_player.remove(c)
        if amount_sent < amount:
            # check player has nothing left if underpaying
            assert from_player.get_money() == 0, "Player underpaid but has cash"
            assert from_player.get_property_as_cash() == 0, (
                "Player underpaid but has assets"
            )

        for c in cards:
            if isinstance(c, PropertyCard):
                to_player.add_property(c.colour, c)
            elif isinstance(c, WildPropertyCard):
                colour = to_player.pick_colour_for_recieved_wildcard(c)
                to_player.add_property(colour, c)
            else:
                to_player.add_money(c)

    def discard(self, card: Card) -> None:
        self.discarded.append(card)


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
