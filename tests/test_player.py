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


def test_money_5_1() -> None:
    p = Player("test")
    p.add_money(mc5 := MoneyCard(5))
    p.add_money(mc1 := MoneyCard(1))
    assert p.get_money() == 6

    # minimising overpayment only passes this test
    exp = {
        0: [],
        1: [mc1],
        2: [mc5],
        3: [mc5],
        4: [mc5],
        5: [mc5],
        6: [mc5, mc1],
        7: [mc5, mc1],
        8: [mc5, mc1],
    }
    for amount in range(9):
        cards = p.choose_how_to_pay(amount)
        print(f" {amount} {cards}")
        assert cards == exp[amount]


def test_money_2_3_5_10() -> None:
    p = Player("test")
    p.add_money(mc10 := MoneyCard(10))
    p.add_money(mc5 := MoneyCard(5))
    p.add_money(mc3 := MoneyCard(3))
    p.add_money(mc2 := MoneyCard(2))
    assert p.get_money() == 20

    # minimising overpayment only passes this test
    exp = {
        0: [],
        1: [mc2],
        2: [mc2],
        3: [mc3],
        4: [mc5],
        5: [mc5],
        6: [mc5, mc2],
        7: [mc5, mc2],
        8: [mc5, mc3],
        9: [mc10],
        10: [mc10],
        11: [mc10, mc2],
        12: [mc10, mc2],
        13: [mc10, mc3],
        14: [mc10, mc5],
        15: [mc10, mc5],
        16: [mc10, mc5, mc2],
        17: [mc10, mc5, mc2],
        18: [mc10, mc5, mc3],
        19: [mc10, mc5, mc3, mc2],
        20: [mc10, mc5, mc3, mc2],
        21: [mc10, mc5, mc3, mc2],
    }
    for amount in range(22):
        cards = p.choose_how_to_pay(amount)
        print(f" {amount} {cards}")
        assert cards == exp[amount]
