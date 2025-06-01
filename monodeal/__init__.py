from dataclasses import dataclass
from enum import Flag, auto
from typing import Mapping, MutableSequence, Protocol, Sequence


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


class PropertySetProto(Protocol):
    def is_complete(self) -> bool: ...
    def rent_value(self) -> int: ...
    def __len__(self) -> int: ...
    def remove(self, card: Card) -> None: ...


class PlayerProto(Protocol):
    def get_action(self, game: "GameProto", actions_left: int) -> "Action": ...
    def has_won(self) -> bool: ...
    def get_hand(self) -> MutableSequence[Card]: ...
    def get_property_sets(self) -> Mapping[PropertyColour, PropertySetProto]: ...
    def get_money(self) -> int: ...
    def get_money_set(self) -> MutableSequence[Card]: ...
    def add_property(self, card: PropertyCard) -> None: ...
    def add_money(self, card: Card) -> None: ...
    def choose_how_to_pay(self, amount: int) -> Sequence[Card]: ...


class GameProto(Protocol):
    def play(self) -> PlayerProto: ...
    def get_opposition(self, player: PlayerProto) -> Sequence[PlayerProto]: ...
    def player_owes_money(
        self, from_player: PlayerProto, to_player: PlayerProto, amount: int
    ) -> None: ...


@dataclass
class Action:
    player: PlayerProto

    def apply(self, g: GameProto) -> None:
        pass

    def action_count(self) -> int:
        return 1
