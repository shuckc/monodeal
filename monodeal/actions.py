from . import Action, GameProto, PlayerProto, Card, PropertyColour, PropertyCard
from .deck import RentCard, DoubleTheRentCard
from dataclasses import dataclass


@dataclass
class SkipAction(Action):
    def apply(self, g: GameProto) -> None:
        pass

    def action_count(self) -> int:
        return 1


@dataclass
class CardAction(Action):
    card: Card

    def action_count(self) -> int:
        return 1

    def apply(self, g: GameProto) -> None:
        self.player.get_hand().remove(self.card)


@dataclass
class PlayPropertyAction(CardAction):
    colour: PropertyColour
    card: PropertyCard

    def apply(self, g: GameProto) -> None:
        super().apply(g)
        self.player.add_property(self.card)


class DoubleRentAction(CardAction):
    def __init__(
        self,
        player: PlayerProto,
        card: RentCard,
        colour: PropertyColour,
        doublerent: DoubleTheRentCard,
    ):
        self.colour = colour
        self.doublerentcard = doublerent
        self.rentcard = card
        super().__init__(player, card)

    def action_count(self) -> int:
        return 2

    def apply(self, g: GameProto) -> None:
        return None
