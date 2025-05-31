from monodeal.deck import PROPERTY_DECK, MoneyCard
from monodeal.game import Player


def test_haswon() -> None:
    p = Player("test")
    assert not p.has_won()

    for prop in PROPERTY_DECK:
        p.add_property(prop)

    assert len(p.propertysets) == 10
    first = next(iter(p.propertysets.values()))
    assert first.is_complete()

    assert p.has_won()


def test_money() -> None:
    p = Player("test")
    assert p.get_money() == 0
    p.add_money(MoneyCard(5))
    p.add_money(MoneyCard(1))

    assert p.get_money() == 6
