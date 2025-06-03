from monodeal import PropertyCard, PropertyColour, WildPropertyCard
from monodeal.deck import PROPERTY_DECK, MoneyCard
from monodeal.game import Player


def test_haswon() -> None:
    p = Player("test")
    assert not p.has_won()

    for prop in PROPERTY_DECK:
        p.add_property(prop.colour, prop)

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


def test_money_3_1_R() -> None:
    p = Player("test")
    p.add_money(mc3 := MoneyCard(3))
    p.add_money(mc1 := MoneyCard(1))
    pc1 = PropertyCard(PropertyColour.RED, "Red Property1", 3)
    p.add_property(pc1.colour, pc1)
    assert p.get_money() == 4
    assert p.get_property_as_cash() == 3

    # minimising overpayment only passes this test
    exp = {
        0: [],
        1: [mc1],
        2: [mc3],
        3: [mc3],
        4: [mc3, mc1],
        5: [mc3, pc1],
        6: [mc3, pc1],
        7: [mc3, mc1, pc1],
        8: [mc3, mc1, pc1],
    }
    for amount in range(9):
        cards = p.choose_how_to_pay(amount)
        print(f" {amount} {cards}")
        assert cards == exp[amount]


def test_money_3_1_R_GG() -> None:
    p = Player("test")
    p.add_money(mc3 := MoneyCard(3))
    p.add_money(mc1 := MoneyCard(1))
    pc1 = PropertyCard(PropertyColour.RED, "Red Property1", 3)
    p.add_property(pc1.colour, pc1)
    pc2 = PropertyCard(PropertyColour.GREEN, "Green Property1", 4)
    p.add_property(pc2.colour, pc2)
    pc3 = PropertyCard(PropertyColour.GREEN, "Green Property2", 4)
    p.add_property(pc3.colour, pc3)
    pc4 = PropertyCard(PropertyColour.GREEN, "Green Property3", 4)
    p.add_property(pc4.colour, pc4)

    assert p.get_money() == 4
    assert p.get_property_as_cash() == 15

    # minimising overpayment only passes this test
    exp = {
        0: [],
        1: [mc1],
        2: [mc3],
        3: [mc3],
        4: [mc3, mc1],
        5: [mc3, pc1],
        6: [mc3, pc1],
        7: [mc3, mc1, pc1],
        8: [mc3, mc1, pc4],
        # for 9 is 1GG (cp=-1,rv=-5,op=0,-2) really better than 3RG (cp=-1,rv=-5,op=1,0) ??
        9: [mc1, pc3, pc4],
        10: [mc3, pc1, pc4],
    }
    for amount in range(11):
        cards = p.choose_how_to_pay(amount)
        print(f" {amount} {cards}")
        assert cards == exp[amount]


def test_money_WPC() -> None:
    p = Player("test")
    pc1 = WildPropertyCard(PropertyColour.ALL, 0)
    pc2 = PropertyCard(PropertyColour.BROWN, "Old Road", 1)
    p.add_property(PropertyColour.RED, pc1)
    p.add_property(PropertyColour.BROWN, pc2)
    cards = p.choose_how_to_pay(5)
    assert cards == [pc2]
