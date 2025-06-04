from copy import copy

import pytest

from monodeal import (
    HotelCard,
    HouseCard,
    PropertyCard,
    PropertyColour,
    WildPropertyCard,
)
from monodeal.game import PropertySet


def test_property_set() -> None:
    p = PropertySet(PropertyColour.GREEN)
    assert p.rent_value() == 0

    p.add_property(PropertyCard(PropertyColour.GREEN, "Bond Street", 4))
    assert not p.is_complete()
    assert p.rent_value() == 2

    with pytest.raises(AssertionError):
        p.add_property(HouseCard())

    with pytest.raises(AssertionError):
        p.add_property(HotelCard())

    p.add_property(PropertyCard(PropertyColour.GREEN, "Regent Street", 4))
    assert not p.is_complete()
    assert p.rent_value() == 4

    p.add_property(poxf := PropertyCard(PropertyColour.GREEN, "Oxford Street", 4))
    assert p.is_complete()
    assert p.rent_value() == 7

    with pytest.raises(AssertionError):
        p.add_property(HotelCard())

    p.add_property(house := HouseCard())

    with pytest.raises(AssertionError):
        p.add_property(HouseCard())

    assert p.is_complete()
    assert p.rent_value() == 10

    p.add_property(hotel := HotelCard())

    with pytest.raises(AssertionError):
        p.add_property(HotelCard())

    assert p.is_complete()
    assert p.rent_value() == 15

    # check removals
    p.remove(poxf)
    assert not p.is_complete()
    assert p.rent_value() == 4  # still has house, hotel but not contributing to rent

    p.add_property(poxf)
    assert p.is_complete()
    assert p.rent_value() == 15

    # check copy.copy()
    p2 = copy(p)
    p2.remove(hotel)
    p2.remove(house)
    p2.remove(poxf)

    assert p.is_complete()
    assert p.rent_value() == 15

    assert not p2.is_complete()
    assert p2.rent_value() == 4


def test_property_set_rainbow_wildcard_has_no_rent() -> None:
    p = PropertySet(PropertyColour.GREEN)
    assert p.rent_value() == 0

    # stays at zero rent
    # https://hasbro-new.custhelp.com/app/answers/detail/a_id/941
    p.add_property(WildPropertyCard(PropertyColour.ALL, 0))
    assert p.rent_value() == 0

    # jumps to 2 property rent
    p.add_property(PropertyCard(PropertyColour.GREEN, "G1", 4))
    assert p.rent_value() == 4


def test_property_set_rainbow_wildcard_not_complete() -> None:
    p = PropertySet(PropertyColour.BROWN)
    assert p.rent_value() == 0

    # https://hasbro-new.custhelp.com/app/answers/detail_uk/a_id/942/
    # stays incomplete
    p.add_property(WildPropertyCard(PropertyColour.ALL, 0))
    p.add_property(wpc1 := WildPropertyCard(PropertyColour.ALL, 0))
    assert p.rent_value() == 0
    assert not p.is_complete()

    # one two-colour wildcard, one rainbow will complete
    p.remove(wpc1)
    p.add_property(WildPropertyCard(PropertyColour.BROWN | PropertyColour.PALEBLUE, 1))
    assert p.is_complete()
