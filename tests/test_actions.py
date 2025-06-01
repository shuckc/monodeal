from monodeal import PropertyColour
from monodeal.actions import (
    BirthdayAction,
    DepositAction,
    PlayPropertyAction,
    generate_actions,
)
from monodeal.deck import MONEY_DECK, PROPERTY_DECK, BirthdayCard, MoneyCard
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
    assert p.get_money_set() == [m1]
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
        DepositAction(player=p2, card=b),
        BirthdayAction(player=p2, card=b),
    ]
    assert p1.get_money() == 1
    assert p2.get_money() == 0
    actions[1].apply(g)

    assert p1.get_money() == 0
    assert p2.get_money() == 1
