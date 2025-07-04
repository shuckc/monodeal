from dataclasses import dataclass
from enum import Flag, auto
from typing import Mapping, MutableSequence, Protocol, Sequence

from .deck import (
    Card,
    HotelCard,
    HouseCard,
    PropertyCard,
    PropertyColour,
    WildPropertyCard,
)
from .propertyset import PropertySet


class Variations(Flag):
    FORCE_UNPLACED_PROPERTY_AS_CASH = auto()
    ALLOW_QUAD_RENT = auto()


class PlayerProto(Protocol):
    name: str

    def deal_card(self, card: Card) -> None: ...
    def get_action(self, game: "GameProto", actions_left: int) -> "Action": ...
    def has_won(self) -> bool: ...
    def get_hand(self) -> MutableSequence[Card]: ...
    def get_property_sets(self) -> Mapping[PropertyColour, PropertySet]: ...
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
    def add_property_set(self, propertyset: PropertySet) -> None: ...
    def remove_property_set(self, propertyset: PropertySet) -> None: ...
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
