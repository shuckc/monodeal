from monodeal.deck import PROPERTY_DECK
from monodeal.game import Player, Game, generate_actions
from monodeal.actions import PlayPropertyAction
from monodeal import PropertyColour


def test_haswon() -> None:
    p = Player("test")
    assert not p.has_won()

    for prop in PROPERTY_DECK:
        p.add_property(prop)

    assert len(p.propertysets) == 10
    first = next(iter(p.propertysets.values()))
    assert first.is_complete()

    assert p.has_won()


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
