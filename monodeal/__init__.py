from typing import Protocol, Sequence, Mapping, MutableSequence
from dataclasses import dataclass
from enum import Flag, auto


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
    def get_rent(self) -> int: ...
    def __len__(self) -> int: ...


class PlayerProto(Protocol):
    def get_action(self, game: "GameProto", actions_left: int) -> "Action": ...
    def has_won(self) -> bool: ...
    def get_hand(self) -> MutableSequence[Card]: ...
    def get_property_sets(self) -> Mapping[PropertyColour, PropertySetProto]: ...
    def add_property(self, card: PropertyCard) -> None: ...


class GameProto(Protocol):
    def play(self) -> PlayerProto: ...
    def get_opposition(self, player: PlayerProto) -> Sequence[PlayerProto]: ...


@dataclass
class Action:
    player: PlayerProto

    def apply(self, g: GameProto) -> None:
        pass

    def action_count(self) -> int:
        return 1
