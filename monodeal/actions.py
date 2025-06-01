from dataclasses import dataclass

from . import (
    Action,
    Card,
    GameProto,
    PlayerProto,
    PropertyCard,
    PropertyColour,
)
from .deck import BirthdayCard, DoubleTheRentCard, RentCard


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


class DepositAction(CardAction):
    def apply(self, g: GameProto) -> None:
        super().apply(g)
        self.player.add_money(self.card)


class BirthdayAction(CardAction):
    # all other players must send us 2M
    def apply(self, g: GameProto) -> None:
        for p in g.get_opposition(self.player):
            g.player_owes_money(p, self.player, 2)


def generate_actions(
    game: GameProto, player: PlayerProto, actions_left: int
) -> list[Action]:
    actions: list[Action] = []
    # opposition = game.get_opposition(player)

    for c in player.get_hand():
        if isinstance(c, PropertyCard):
            actions.append(PlayPropertyAction(player=player, colour=c.colour, card=c))
        else:
            actions.append(DepositAction(player=player, card=c))
            if isinstance(c, BirthdayCard):
                actions.append(BirthdayAction(player=player, card=c))

    return actions
