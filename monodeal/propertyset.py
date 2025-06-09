from typing import Iterator, Self, Sequence

from .deck import (
    ALLOWED_BUILDINGS,
    RENTS,
    Card,
    HotelCard,
    HouseCard,
    PropertyCard,
    PropertyColour,
    WildPropertyCard,
)


class PropertySet:
    def __init__(self, colour: PropertyColour):
        self.colour: PropertyColour = colour
        self.properties: list[PropertyCard] = []
        self.wilds: list[WildPropertyCard] = []
        self.hotel: HotelCard | None = None
        self.house: HouseCard | None = None
        self.rents: Sequence[int] = RENTS[self.colour]

    def __iter__(self) -> Iterator[Card]:
        for p in self.properties:
            yield p
        for w in self.wilds:
            yield w
        if self.house:
            yield self.house
        if self.hotel:
            yield self.hotel

    def is_complete(self) -> bool:
        if len(self.properties) == 0:
            if all(w.colours == PropertyColour.ALL for w in self.wilds):
                return False
        return len(self.rents) <= len(self.properties) + len(self.wilds)

    def get_colour(self) -> PropertyColour:
        return self.colour

    def rent_value(self) -> int:
        # TODO: hotel + house logic
        card_count = len(self.properties) + len(self.wilds)
        if card_count == 0:
            return 0
        if len(self.properties) == 0:
            if all(w.colours == PropertyColour.ALL for w in self.wilds):
                return 0
        base = self.rents[min(card_count, len(self.rents)) - 1]
        if not self.is_complete():
            return base
        if self.house:
            base = base + 3
            if self.hotel:
                base = base + 5
        return base

    def add_property(self, card: Card) -> Self:
        if isinstance(card, HouseCard):
            assert self.colour in ALLOWED_BUILDINGS
            assert self.is_complete()
            assert self.house is None
            self.house = card
        elif isinstance(card, HotelCard):
            assert self.colour in ALLOWED_BUILDINGS
            assert self.is_complete()
            assert self.house is not None
            assert self.hotel is None
            self.hotel = card
        elif isinstance(card, PropertyCard):
            assert card.colour == self.colour
            self.properties.append(card)
        elif isinstance(card, WildPropertyCard):
            assert self.colour in card.colours
            self.wilds.append(card)
        else:
            raise ValueError(card)
        return self

    def __len__(self) -> int:
        return (
            len(self.properties)
            + len(self.wilds)
            + (1 if self.house else 0)
            + (1 if self.hotel else 0)
        )

    def __repr__(self) -> str:
        return f"PS({self.colour.name},{len(self.properties) + len(self.wilds)}/{len(self.rents)},{','.join(p.property_name for p in self.properties)},{','.join(p.name for p in self.wilds)},{'+House' if self.house else '-'},{'+Hotel' if self.hotel else '-'})"

    def remove(self, card: Card) -> None:
        if isinstance(card, HouseCard):
            assert self.house == card
            self.house = None
        elif isinstance(card, HotelCard):
            assert self.hotel == card
            self.hotel = None
        elif isinstance(card, PropertyCard):
            self.properties.remove(card)
        elif isinstance(card, WildPropertyCard):
            self.wilds.remove(card)
        else:
            raise ValueError(card)

    def __copy__(self) -> "PropertySet":
        c = PropertySet(self.colour)
        for card in self.properties:
            c.properties.append(card)
        for wc in self.wilds:
            c.wilds.append(wc)
        c.house = self.house
        c.hotel = self.hotel
        return c

    def can_build_house(self) -> bool:
        return (
            self.is_complete()
            and self.colour in ALLOWED_BUILDINGS
            and self.house is None
        )

    def can_build_hotel(self) -> bool:
        return (
            self.is_complete()
            and self.colour in ALLOWED_BUILDINGS
            and self.house is not None
            and self.hotel is None
        )
