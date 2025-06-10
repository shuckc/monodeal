import copy
import random
from collections import Counter, defaultdict, deque
from itertools import chain, combinations
from typing import Iterable, Mapping, MutableSequence, Sequence, Tuple

from . import (
    Action,
    GameProto,
    PlayerProto,
    Variations,
)
from .actions import DealBreakerAction, SkipAction, generate_actions
from .deck import (
    ALLOWED_BUILDINGS,
    DECK,
    Card,
    HotelCard,
    HouseCard,
    JustSayNoCard,
    PropertyCard,
    PropertyColour,
    WildPropertyCard,
)
from .propertyset import PropertySet


def cash_value(cards: Iterable[Card]) -> int:
    return sum(card.cash for card in cards)


class default_copydict(defaultdict[PropertySet, PropertySet]):
    def __missing__(self, key: PropertySet) -> PropertySet:
        value = copy.copy(key)
        self[key] = value
        return value


def property_cps_rv_without(
    pss: dict[Card, PropertySet], without: Sequence[Card]
) -> Tuple[int, int]:
    # precondition: each card in without should be in pss
    sets: dict[Card, PropertySet] = {}
    if without == []:
        # optimisation if we do not need to remove any property
        sets = pss
    else:
        remap: dict[PropertySet, PropertySet] = default_copydict()
        for card, ps in pss.items():
            ps_new = remap[ps]
            sets[card] = ps_new
            if card in without:
                ps_new.remove(card)

    complete_sets = 0
    rent_value = 0
    for ps in set(sets.values()):
        if ps.is_complete():
            complete_sets += 1
        rent_value += ps.rent_value()

    return complete_sets, rent_value


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
        self.unallocated_buildings: list[HouseCard | HotelCard] = []

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

    def get_property_sets(self) -> Mapping[PropertyColour, PropertySet]:
        return self.propertysets

    def has_won(self) -> bool:
        complete_sets, _ = property_cps_rv_without(self.cards_to_ps, [])
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

    def add_unallocated_building(self, card: HouseCard | HotelCard) -> None:
        self.unallocated_buildings.append(card)

    def remove(self, card: Card) -> None:
        ps: PropertySet | None = self.cards_to_ps.get(card, None)
        if ps:
            ps.remove(card)
            self.cards_to_ps.pop(card)
        elif isinstance(card, HouseCard) or isinstance(card, HotelCard):
            if card in self.unallocated_buildings:
                self.unallocated_buildings.remove(card)
            else:
                self.cash.remove(card)
        else:
            self.cash.remove(card)

    def get_money(self) -> int:
        return cash_value(self.cash)

    def get_property_as_cash(self) -> int:
        return cash_value(self.cards_to_ps.keys()) + cash_value(
            self.unallocated_buildings
        )

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

        if to_pay > cash_value(cards):
            cards.extend(self.unallocated_buildings)

        # if we can pay this amount without dipping into property, do so
        # since it makes the powerset much smaller
        for include_complete in False, True:
            if to_pay > cash_value(cards):
                print(f"including complete: {include_complete}")
                for c, ps in self.cards_to_ps.items():
                    if (
                        isinstance(c, WildPropertyCard)
                        and c.colours == PropertyColour.ALL
                    ):
                        continue
                    if ps.is_complete() == include_complete:
                        cards.append(c)

        assert len(set(cards)) == len(cards)

        # iterate over the powerset evaluating a metric for each
        # solution with an overpay >= 0
        #
        # rank options by minimising (cps,rv,sr,overpay)
        #   cps - reduction in complete property sets
        #   rv  - reduction in rental value
        #   overpay - cash sent above to_pay
        #   sc  - smallest cash card
        # e.g. a spend of [1,3,10] [Green->[G,G,G,H,H], Red->[R]]
        #  for a target to_pay=6 could be [3,R] at (0,2,0)
        #        target to_pay=20 could be [10,3,1,H,H,R] (0,7,1)
        #        target to_pay=22 could be [10,3,1,H,H,R,G] (1,9,0)
        #
        # order of cards does not matter

        # baseline metrics, with all player's cards
        sc_orig = smallest_cash_remaining_without(cards, [])
        cps_orig, rv_orig = property_cps_rv_without(self.cards_to_ps, [])

        least_score = (9999, 0, 0, 0)
        valid_minimal_sets: list[set[Card]] = []

        for cs in card_powerset(cards):
            cv = cash_value(cs)
            overpay = cv - to_pay
            if overpay < 0:
                continue

            # if a subset of this combination was viable, this set is strictly worse, skip eval
            if any(ms.issubset(cs) for ms in valid_minimal_sets):
                continue
            valid_minimal_sets.append(set(cs))

            # print(f"{self} checking {cs} with cv={cv} overpayment={overpay}")
            cs_props = [c for c in cs if c in self.cards_to_ps]
            cs_cash = [c for c in cs if c in self.cash]

            # calculate cps, rv, sc
            cps = cps_orig
            rv = rv_orig
            sc = sc_orig
            if cs_props:
                cps, rv = property_cps_rv_without(self.cards_to_ps, cs_props)
            if cs_cash:
                sc = smallest_cash_remaining_without(self.cash, cs_cash)

            score = (cps_orig - cps, rv_orig - rv, overpay, sc - sc_orig)
            print(
                f"{self} scored {cs} with cv={cv} overpayment={overpay} as {score} vs. least {least_score}"
            )

            if score <= least_score:
                print(f" ** improves score {score} < {least_score}")

                # OK candidate
                best = cs
                least_score = score
                # exit early if optimal
                if overpay == 0 and sc == sc_orig and rv == rv_orig and cps == cps_orig:
                    break
        print(
            f"{self} choose_how_to_pay() solver for {amount} (to_pay={to_pay}) chose {best} with ps,rv,overpay,sr={least_score}"
        )
        return list(best)

    def pick_colour_for_recieved_wildcard(
        self, card: WildPropertyCard
    ) -> PropertyColour:
        # TODO: consider putting recieved wildcard in an incomplete PS, moving it to complete a
        # set only on our own turn, to avoid DealBreaker risk prior to our go?

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

    def pick_colour_for_recieved_building(
        self, card: HouseCard | HotelCard
    ) -> PropertyColour | None:
        # maxmimise increase in rv, or leave unallocated if cannot yet be played
        is_house = isinstance(card, HouseCard)

        best: PropertyColour | None = None
        rv_incr = 0
        for pc in ALLOWED_BUILDINGS:
            ps = self._get_or_create_ps(pc)
            if (is_house and ps.can_build_house()) or (
                not is_house and ps.can_build_hotel()
            ):
                rv_base = ps.rent_value()
                rv_new = copy.copy(ps).add_property(card).rent_value()
                print(
                    f"{self} recieved {card} scoring {pc} takes rv from {rv_base} to {rv_new}"
                )
                if rv_new - rv_base > rv_incr:
                    rv_incr = rv_new - rv_base
                    best = pc
        print(f"{self} chose {card} as {best} with rv_incr {rv_incr}")
        return best

    def add_property_set(self, propertyset: PropertySet) -> None:
        # we might already have a propertyset for this colour?
        colour = propertyset.get_colour()

        existing_ps = self.propertysets.get(colour, None)
        if existing_ps is None:
            print("No existing ps")
            self.propertysets[colour] = propertyset
            for card in propertyset:
                self.cards_to_ps[card] = propertyset
            return

        # merge propertyset properties first, then wildcards
        for card in propertyset.properties:
            self.add_property(colour, card)

        for wild in propertyset.wilds:
            c2 = self.pick_colour_for_recieved_wildcard(wild)
            self.add_property(c2, wild)

        if propertyset.house is not None:
            if existing_ps.can_build_house():
                self.add_property(colour, propertyset.house)
            else:
                c3 = self.pick_colour_for_recieved_building(propertyset.house)
                if c3:
                    self.add_property(c3, propertyset.house)
                else:
                    self.add_money(propertyset.house)

        if propertyset.hotel is not None:
            if existing_ps.can_build_hotel():
                self.add_property(colour, propertyset.hotel)
            else:
                c4 = self.pick_colour_for_recieved_building(propertyset.hotel)
                if c4:
                    self.add_property(c4, propertyset.hotel)
                else:
                    self.add_money(propertyset.hotel)

    def remove_property_set(self, propertyset: PropertySet) -> None:
        cards_to_remove: set[Card] = set()
        for card, ps in self.cards_to_ps.items():
            if ps == propertyset:
                cards_to_remove.add(card)
        for c in cards_to_remove:
            self.cards_to_ps.pop(c)
        self.propertysets.pop(propertyset.get_colour())

    def should_stop_action(self, action: "Action") -> bool:
        if isinstance(action, DealBreakerAction):
            return True

        return False


class Game(GameProto):
    def __init__(
        self,
        players: list[Player] = [],
        random: random.Random = random.Random(),
        variations: Variations = Variations(0),
    ):
        self.players = players
        self.draw: deque[Card] = deque()
        self.discarded: deque[Card] = deque()
        self.random = random
        self.variations = variations

    def deal_to(self, p: PlayerProto) -> None:
        if len(self.draw) == 0:
            print(f"reshuffling {len(self.discarded)} discarded cards")
            self.draw.extend(self.discarded)
            self.discarded.clear()
            self.random.shuffle(self.draw)
        p.deal_card(self.draw.popleft())

    def _play(self) -> PlayerProto:
        # initial setup
        self.discarded.extend(DECK)
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

                    self.audit()

                    if p.has_won():
                        print(f"{p} has won!")
                        return p

                while len(p.hand) > 7:
                    d = p.get_discard()
                    print(f"{p} discarded {d}")
                    self.discarded.append(d)

                self.audit()

    def play(self) -> PlayerProto:
        try:
            return self._play()
        except:
            print("==== CRASHED - state was ====")
            print(f"draw: {self.draw}")
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
        amount_sent = 0

        for c in cards:
            from_player.remove(c)
            amount_sent += c.cash

        if amount_sent < amount:
            # check player has nothing left if underpaying
            assert from_player.get_money() == 0, "Player underpaid but has cash"
            assert from_player.get_property_as_cash() == 0, (
                "Player underpaid but has assets"
            )

        # TODO: to optimise the layout of recieved payment, report in order:
        # 1) PropertyCard, 2) WildPropertyCard, 3) HouseCard, 4) HotelCard
        for c in cards:
            if isinstance(c, PropertyCard):
                to_player.add_property(c.colour, c)
            elif isinstance(c, WildPropertyCard):
                colour = to_player.pick_colour_for_recieved_wildcard(c)
                to_player.add_property(colour, c)
            elif isinstance(c, HouseCard) or isinstance(c, HotelCard):
                optional_colour = to_player.pick_colour_for_recieved_building(c)
                if optional_colour is not None:
                    to_player.add_property(optional_colour, c)
                else:
                    # VARIATION: where to store unallocated house/hotel?
                    # storing in unallocated will trigger
                    # calls to player.pick_colour_for_recieved_building() later
                    if Variations.FORCE_UNPLACED_PROPERTY_AS_CASH in self.variations:
                        print(f"cash: unplaced property becomes cash {c}")
                        to_player.add_money(c)
                    else:
                        to_player.add_unallocated_building(c)
                        raise ValueError("store unallocated house/hotel?!")
            else:
                to_player.add_money(c)

    def discard(self, card: Card) -> None:
        self.discarded.append(card)

    def check_stop_action(self, p: PlayerProto, a: Action) -> bool:
        stop_cards = [card for card in p.get_hand() if isinstance(card, JustSayNoCard)]
        if len(stop_cards) > 0:
            card = stop_cards[0]
            if p.should_stop_action(a):
                p.get_hand().remove(card)
                self.discard(card)
                return True
        return False

    def audit(self) -> None:
        cards = len(self.discarded) + len(self.draw)
        for player in self.players:
            cards += len(player.hand) + len(player.cash) + len(player.cards_to_ps)
        print(f"audit: {cards}")
        assert cards == 106


class ConsolePlayer(Player):
    pass


class RandomPlayer(Player):
    pass


if __name__ == "__main__":
    winners: Counter[str] = Counter()

    for i in range(100):
        a: Player = ConsolePlayer("A")
        b: Player = RandomPlayer("B")
        g: Game = Game(
            players=[a, b], variations=Variations.FORCE_UNPLACED_PROPERTY_AS_CASH
        )
        winner = g.play()
        print(winner)
        winners[winner.name] += 1
    print(winners)
