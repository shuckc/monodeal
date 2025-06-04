from dataclasses import dataclass

from . import (
    Action,
    Card,
    GameProto,
    HotelCard,
    HouseCard,
    PlayerProto,
    PropertyCard,
    PropertyColour,
    WildPropertyCard,
)
from .deck import (
    BirthdayCard,
    DealBreakerCard,
    DebtCollectorCard,
    DoubleTheRentCard,
    ForcedDealCard,
    JustSayNoCard,
    MoneyCard,
    PassGoCard,
    RainbowRentCard,
    RentCard,
    SlyDealCard,
)


@dataclass
class SkipAction(Action):
    def apply(self, g: GameProto) -> None:
        pass

    def action_count(self) -> int:
        return 1


@dataclass
class DiscardAction(Action):
    card: Card

    def action_count(self) -> int:
        return 1

    def apply(self, g: GameProto) -> None:
        # move card from hand to discard pile
        self.player.get_hand().remove(self.card)
        g.discard(self.card)


@dataclass
class PlayPropertyAction(Action):
    card: PropertyCard | WildPropertyCard | HouseCard | HotelCard
    colour: PropertyColour

    def apply(self, g: GameProto) -> None:
        # move from hand to property sets
        self.player.get_hand().remove(self.card)
        self.player.add_property(self.colour, self.card)

    def action_count(self) -> int:
        return 1


class DoubleRentAction(DiscardAction):
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


class DepositAction(DiscardAction):
    def apply(self, g: GameProto) -> None:
        # move hand -> cash
        self.player.get_hand().remove(self.card)
        self.player.add_money(self.card)


class BirthdayAction(DiscardAction):
    # all other players must send us 2M
    def apply(self, g: GameProto) -> None:
        super().apply(g)
        for p in g.get_opposition(self.player):
            g.player_owes_money(p, self.player, 2)


@dataclass
class DebtCollectorAction(DiscardAction):
    # nominated player must send us 5M
    opponent: PlayerProto

    def apply(self, g: GameProto) -> None:
        super().apply(g)
        g.player_owes_money(self.opponent, self.player, 5)


@dataclass
class PassGoAction(DiscardAction):
    def apply(self, g: GameProto) -> None:
        super().apply(g)
        g.deal_to(self.player)
        g.deal_to(self.player)


def generate_actions(
    game: GameProto, player: PlayerProto, actions_left: int
) -> list[Action]:
    actions: list[Action] = []
    # opposition = game.get_opposition(player)

    for c in player.get_hand():
        if isinstance(c, PropertyCard):
            actions.append(PlayPropertyAction(player=player, colour=c.colour, card=c))
        else:
            if isinstance(c, BirthdayCard):
                actions.append(BirthdayAction(player=player, card=c))
            elif isinstance(c, DebtCollectorCard):
                for op in game.get_opposition(player):
                    actions.append(
                        DebtCollectorAction(
                            player=player,
                            card=c,
                            opponent=op,
                        )
                    )
            elif isinstance(c, WildPropertyCard):
                # one action for each possible colour
                for col in c.colours:
                    actions.append(
                        PlayPropertyAction(player=player, colour=col, card=c)
                    )
            elif isinstance(c, MoneyCard):
                actions.append(DepositAction(player=player, card=c))
            elif isinstance(c, SlyDealCard):
                pass
            elif isinstance(c, JustSayNoCard):
                pass
            elif isinstance(c, RentCard):
                pass
            elif isinstance(c, RainbowRentCard):
                pass
            elif isinstance(c, ForcedDealCard):
                pass
            elif isinstance(c, DoubleTheRentCard):
                pass
            elif isinstance(c, PassGoCard):
                actions.append(PassGoAction(player=player, card=c))
            elif isinstance(c, DealBreakerCard):
                pass
            elif isinstance(c, HouseCard):
                for ps in player.get_property_sets().values():
                    if ps.can_build_house():
                        actions.append(
                            PlayPropertyAction(
                                player=player, card=c, colour=ps.get_colour()
                            )
                        )
            elif isinstance(c, HotelCard):
                for ps in player.get_property_sets().values():
                    if ps.can_build_hotel():
                        actions.append(
                            PlayPropertyAction(
                                player=player, card=c, colour=ps.get_colour()
                            )
                        )

            else:
                raise ValueError(c)
                # actions.append(DepositAction(player=player, card=c))

    return actions
