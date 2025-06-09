from dataclasses import dataclass
from enum import Flag, auto
from typing import Iterable, Mapping, MutableSequence, Protocol, Sequence


class PropertyColour(Flag):
    UTILITY = auto()
    STATION = auto()
    BROWN = auto()
    PALEBLUE = auto()
    ORANGE = auto()
    MAGENTA = auto()
    YELLOW = auto()
    RED = auto()
    GREEN = auto()
    DARKBLUE = auto()
    ALL = (
        UTILITY
        | STATION
        | BROWN
        | PALEBLUE
        | ORANGE
        | MAGENTA
        | YELLOW
        | RED
        | GREEN
        | DARKBLUE
    )


class Variations(Flag):
    FORCE_UNPLACED_PROPERTY_AS_CASH = auto()
    ALLOW_QUAD_RENT = auto()


class Card:
    def __init__(self, cash: int, name: str):
        self.cash = cash
        self.name = name

    def __repr__(self) -> str:
        return self.name


class PropertyCard(Card):
    def __init__(self, colour: PropertyColour, name: str, cash: int):
        self.colour = colour
        self.property_name = name
        super().__init__(cash, f"PropertyCard[{colour.name},{name!r}]")


class WildPropertyCard(Card):
    def __init__(self, colours: PropertyColour, cash: int):
        super().__init__(cash, f"PropertyWildCard[{colours}]")
        self.colours = colours
        assert len(colours) > 1  # py3.11+


class HouseCard(Card):
    def __init__(self) -> None:
        super().__init__(3, "HouseCard")


class HotelCard(Card):
    def __init__(self) -> None:
        super().__init__(4, "HotelCard")


class PropertySetProto(Iterable[Card], Protocol):
    def is_complete(self) -> bool: ...
    def rent_value(self) -> int: ...
    def __len__(self) -> int: ...
    def remove(self, card: Card) -> None: ...
    def can_build_house(self) -> bool: ...
    def can_build_hotel(self) -> bool: ...
    def get_colour(self) -> PropertyColour: ...


class PlayerProto(Protocol):
    name: str

    def deal_card(self, card: Card) -> None: ...
    def get_action(self, game: "GameProto", actions_left: int) -> "Action": ...
    def has_won(self) -> bool: ...
    def get_hand(self) -> MutableSequence[Card]: ...
    def get_property_sets(self) -> Mapping[PropertyColour, PropertySetProto]: ...
    def get_money(self) -> int: ...
    def get_property_as_cash(self) -> int: ...
    def add_property(
        self,
        colour: PropertyColour,
        card: PropertyCard | WildPropertyCard | HouseCard | HotelCard,
    ) -> None: ...
    def add_money(self, card: Card) -> None: ...
    def add_unallocated_building(self, card: HouseCard | HotelCard) -> None: ...
    def choose_how_to_pay(self, amount: int) -> Sequence[Card]: ...
    def pick_colour_for_recieved_wildcard(
        self, card: WildPropertyCard
    ) -> PropertyColour: ...
    def pick_colour_for_recieved_building(
        self, card: HouseCard | HotelCard
    ) -> PropertyColour | None: ...
    def remove(self, card: Card) -> None: ...
    def add_property_set(self, propertyset: PropertySetProto) -> None: ...
    def remove_property_set(self, propertyset: PropertySetProto) -> None: ...
    def should_stop_action(self, action: "Action") -> bool: ...


class GameProto(Protocol):
    variations: Variations

    def play(self) -> PlayerProto: ...
    def get_opposition(self, player: PlayerProto) -> Sequence[PlayerProto]: ...
    def player_owes_money(
        self, from_player: PlayerProto, to_player: PlayerProto, amount: int
    ) -> None: ...
    def discard(self, card: Card) -> None: ...
    def deal_to(self, p: PlayerProto) -> None: ...
    def check_stop_action(self, p: PlayerProto, a: "Action") -> bool: ...


@dataclass
class Action:
    player: PlayerProto

    def apply(self, g: GameProto) -> None:
        pass

    def action_count(self) -> int:
        return 1
