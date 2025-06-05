from dataclasses import dataclass
from typing import Sequence, TypeVar

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
    Variations,
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


@dataclass
class RentAction(DiscardAction):
    propertyset: PropertySetProto
    double_rent: DoubleTheRentCard | None
    quad_rent: DoubleTheRentCard | None
    target: PlayerProto | None

    def action_count(self) -> int:
        return (
            1
            + (0 if self.double_rent is None else 1)
            + (0 if self.quad_rent is None else 1)
        )

    def apply(self, g: GameProto) -> None:
        rent = self.propertyset.rent_value()
        rent *= 1 if self.double_rent is None else 2
        rent *= 1 if self.quad_rent is None else 2
        rent_target = (
            [self.target] if self.target is not None else g.get_opposition(self.player)
        )

        for p in rent_target:
            g.player_owes_money(p, self.player, rent)

        # discard multiple cards
        for card in [self.card, self.double_rent, self.quad_rent]:
            if card is None:
                continue
            self.player.get_hand().remove(card)
            g.discard(card)


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
    target: PlayerProto

    def apply(self, g: GameProto) -> None:
        super().apply(g)
        g.player_owes_money(self.target, self.player, 5)


@dataclass
class PassGoAction(DiscardAction):
    def apply(self, g: GameProto) -> None:
        super().apply(g)
        g.deal_to(self.player)
        g.deal_to(self.player)


X = TypeVar("X")


def maybe_index(items: Sequence[X], idx: int, default: X | None = None) -> X | None:
    try:
        return items[idx]
    except IndexError:
        return default


def generate_actions(
    game: GameProto, player: PlayerProto, actions_left: int
) -> list[Action]:
    actions: list[Action] = []
    # opposition = game.get_opposition(player)

    # check whole hand for actions that act on multiple cards
    double_rent_cards = [
        card for card in player.get_hand() if isinstance(card, DoubleTheRentCard)
    ]
    double_rent = maybe_index(double_rent_cards, 0)
    quad_rent = (
        maybe_index(double_rent_cards, 1)
        if Variations.ALLOW_QUAD_RENT in game.variations
        else None
    )

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
                            target=op,
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
                for col in c.colours:
                    ps = player.get_property_sets().get(col)
                    if ps is None or ps.rent_value() == 0:
                        continue
                    actions.append(
                        RentAction(
                            player=player,
                            propertyset=ps,
                            card=c,
                            double_rent=double_rent,
                            quad_rent=quad_rent,
                            target=None,
                        )
                    )

            elif isinstance(c, RainbowRentCard):
                for col in c.colours:
                    ps = player.get_property_sets().get(col)
                    if ps is None or ps.rent_value() == 0:
                        continue
                    for t in game.get_opposition(player):
                        actions.append(
                            RentAction(
                                player=player,
                                propertyset=ps,
                                card=c,
                                double_rent=double_rent,
                                quad_rent=quad_rent,
                                target=t,
                            )
                        )

            elif isinstance(c, ForcedDealCard):
                pass
            elif isinstance(c, DoubleTheRentCard):
                # this is dealt with by the RentCard handler
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
