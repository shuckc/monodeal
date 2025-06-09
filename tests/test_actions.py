from monodeal.actions import (
    BirthdayAction,
    DealBreakerAction,
    DepositAction,
    PlayPropertyAction,
    generate_actions,
)
from monodeal.deck import (
    MONEY_DECK,
    PROPERTY_DECK,
    BirthdayCard,
    DealBreakerCard,
    HotelCard,
    HouseCard,
    MoneyCard,
    PropertyCard,
    PropertyColour,
    WildPropertyCard,
)
from monodeal.game import Game, Player


def test_property_actions() -> None:
    p = Player("test")
    g = Game([p])

    p0 = PROPERTY_DECK[0]
    assert str(p0) == "PropertyCard[UTILITY,'Water Works']"
    p.deal_card(p0)

    actions = generate_actions(g, p, 3)
    assert len(actions) == 1
    actions[0] == PlayPropertyAction(player=p, colour=PropertyColour.UTILITY, card=p0)
    assert (
        str(actions[0])
        == "PlayPropertyAction(player=Player test, card=PropertyCard[UTILITY,'Water Works'], colour=<PropertyColour.UTILITY: 1>)"
    )

    actions[0].apply(g)
    assert len(p.get_hand()) == 0
    assert len(p.get_property_sets()) == 1
    ps0 = p.get_property_sets()[PropertyColour.UTILITY]
    assert len(ps0) == 1
    assert not ps0.is_complete()

    p1 = PROPERTY_DECK[1]
    assert str(p1) == "PropertyCard[UTILITY,'Electric Company']"
    p.deal_card(p1)
    actions = generate_actions(g, p, 3)
    assert len(actions) == 1
    actions[0] == PlayPropertyAction(player=p, colour=PropertyColour.UTILITY, card=p1)
    actions[0].apply(g)

    assert len(p.get_hand()) == 0
    assert len(p.get_property_sets()) == 1
    assert ps0.is_complete()


def test_cash_actions() -> None:
    m1 = MONEY_DECK[0]
    p = Player("test")
    g = Game([p])
    assert str(m1) == "MoneyCard[1]"
    p.deal_card(m1)
    actions = generate_actions(g, p, 3)
    assert actions == [DepositAction(player=p, card=m1)]
    assert p.get_money() == 0
    actions[0].apply(g)

    assert p.get_money() == 1
    assert p.cash == [m1]
    assert len(p.get_hand()) == 0


def test_birthday_actions() -> None:
    m1 = MoneyCard(1)
    # m3 = MoneyCard(3)

    b = BirthdayCard()

    p1 = Player("test1")
    p2 = Player("test1")
    g = Game([p1, p2])

    p1.add_money(m1)
    p2.deal_card(b)
    actions = generate_actions(g, p2, 3)
    assert actions == [
        # DepositAction(player=p2, card=b),
        BirthdayAction(player=p2, card=b),
    ]
    assert p1.get_money() == 1
    assert p2.get_money() == 0
    actions[0].apply(g)

    assert p1.get_money() == 0
    assert p2.get_money() == 1


def test_property_build_actions() -> None:
    p = Player("test")
    g = Game([p])

    p0 = PropertyCard(PropertyColour.BROWN, "Old Kent Road", 1)
    p1 = PropertyCard(PropertyColour.BROWN, "Whitechapel Road", 1)
    p2 = HouseCard()
    p3 = HotelCard()

    p.deal_card(p0)
    actions = generate_actions(g, p, 3)
    assert actions == [
        PlayPropertyAction(player=p, colour=PropertyColour.BROWN, card=p0)
    ]
    actions[0].apply(g)

    ps0 = p.get_property_sets()[PropertyColour.BROWN]
    assert len(ps0) == 1
    assert not ps0.is_complete()

    p.deal_card(p1)
    p.deal_card(p2)
    p.deal_card(p3)
    actions = generate_actions(g, p, 3)
    assert actions == [
        PlayPropertyAction(player=p, colour=PropertyColour.BROWN, card=p1)
    ]
    actions[0].apply(g)

    assert len(p.get_hand()) == 2
    assert ps0.is_complete()
    assert len(ps0) == 2

    actions = generate_actions(g, p, 3)
    assert actions == [
        PlayPropertyAction(player=p, colour=PropertyColour.BROWN, card=p2)
    ]
    actions[0].apply(g)
    assert len(ps0) == 3

    actions = generate_actions(g, p, 3)
    assert actions == [
        PlayPropertyAction(player=p, colour=PropertyColour.BROWN, card=p3)
    ]
    actions[0].apply(g)
    assert len(ps0) == 4
    assert ps0.rent_value() == 10


def test_deal_breaker_not_owned() -> None:
    p1 = Player("P1")
    p2 = Player("P2")
    g = Game([p1, p2])

    pc0 = PropertyCard(PropertyColour.BROWN, "Old Kent Road", 1)
    pc1 = PropertyCard(PropertyColour.BROWN, "Whitechapel Road", 1)
    dbc = DealBreakerCard()

    p1.deal_card(dbc)
    p2.add_property(PropertyColour.BROWN, pc0)
    p2.add_property(PropertyColour.BROWN, pc1)

    to_steal = p2.get_property_sets()[PropertyColour.BROWN]
    actions = generate_actions(g, p1, 3)
    assert actions == [
        DealBreakerAction(player=p1, card=dbc, target=p2, propertyset=to_steal)
    ]

    actions[0].apply(g)
    assert p2.get_property_as_cash() == 0
    assert p1.get_property_as_cash() == 2


def test_deal_breaker_ps_merge() -> None:
    p1 = Player("P1")
    p2 = Player("P2")
    g = Game([p1, p2])

    pc0 = PropertyCard(PropertyColour.BROWN, "Old Kent Road", 1)
    pc1 = PropertyCard(PropertyColour.BROWN, "Whitechapel Road", 1)
    pc2 = PropertyCard(PropertyColour.PALEBLUE, "Pentonville Road", 1)
    pc3 = PropertyCard(PropertyColour.PALEBLUE, "The Angel, Islington", 1)

    wp0 = WildPropertyCard(PropertyColour.PALEBLUE | PropertyColour.BROWN, 1)
    # wp1 = WildPropertyCard(PropertyColour.STATION | PropertyColour.PALEBLUE, 4)
    dbc = DealBreakerCard()

    p1.add_property(PropertyColour.PALEBLUE, pc3)
    p1.add_property(PropertyColour.PALEBLUE, pc2)
    # p1.add_property(PropertyColour.PALEBLUE, wp1)
    p1.add_property(PropertyColour.BROWN, pc1)
    p1.deal_card(dbc)

    p2.add_property(PropertyColour.BROWN, pc0)
    p2.add_property(PropertyColour.BROWN, wp0)

    assert not p1.get_property_sets()[PropertyColour.PALEBLUE].is_complete()
    assert not p1.get_property_sets()[PropertyColour.BROWN].is_complete()

    to_steal = p2.get_property_sets()[PropertyColour.BROWN]
    actions = generate_actions(g, p1, 3)
    assert actions == [
        DealBreakerAction(player=p1, card=dbc, target=p2, propertyset=to_steal)
    ]

    actions[0].apply(g)

    assert p1.get_property_sets()[PropertyColour.BROWN].is_complete()
    assert len(p1.get_property_sets()[PropertyColour.BROWN].wilds) == 0

    # verify PALEBLUE got the wildcard
    assert p1.get_property_sets()[PropertyColour.PALEBLUE].is_complete()

    # This does not consider cacade
    # e.g. if PALEBLUE was already complete and pushed out a wildcard
