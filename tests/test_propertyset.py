from copy import copy

import pytest

from monodeal import HotelCard, HouseCard, PropertyCard, PropertyColour
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
