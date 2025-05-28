from monodeal.deck import (
    PROPERTY_DECK,
    MONEY_DECK,
    PROPERTY_WILDCARDS,
    DECK,
    RENT_CARDS,
    ACTION_CARDS,
)


def test_deck() -> None:
    assert len(PROPERTY_DECK) == 28
    assert len(PROPERTY_WILDCARDS) == 11
    assert len(MONEY_DECK) == 20
    assert sum(c.cash for c in MONEY_DECK) == 57
    assert len(RENT_CARDS) == 13
    assert len(ACTION_CARDS) == 34
    # Package says contains 110 cards, however 4 are 'reference' instructional cards
    assert len(DECK) == 110 - 4
