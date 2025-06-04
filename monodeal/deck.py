from typing import Sequence

from . import Card, HotelCard, HouseCard, PropertyCard, PropertyColour, WildPropertyCard
from . import PropertyColour as PC

RENTS: dict[PropertyColour, Sequence[int]] = {
    PropertyColour.UTILITY: [1, 2],
    PropertyColour.STATION: [1, 2, 3, 4],
    PropertyColour.BROWN: [1, 2],
    PropertyColour.PALEBLUE: [1, 2, 3],
    PropertyColour.ORANGE: [1, 3, 5],
    PropertyColour.MAGENTA: [1, 2, 4],
    PropertyColour.YELLOW: [2, 4, 6],
    PropertyColour.RED: [2, 3, 6],
    PropertyColour.GREEN: [2, 4, 7],
    PropertyColour.DARKBLUE: [3, 8],
}

ALLOWED_BUILDINGS = (
    PC.BROWN
    | PC.PALEBLUE
    | PC.ORANGE
    | PC.MAGENTA
    | PC.YELLOW
    | PC.RED
    | PC.GREEN
    | PC.DARKBLUE
)

PROPERTY_DECK = [
    PropertyCard(PropertyColour.UTILITY, "Water Works", 2),
    PropertyCard(PropertyColour.UTILITY, "Electric Company", 2),
    PropertyCard(PropertyColour.STATION, "Liverpool St", 2),
    PropertyCard(PropertyColour.STATION, "Fenchurch St", 2),
    PropertyCard(PropertyColour.STATION, "Kings Cross Station", 2),
    PropertyCard(PropertyColour.STATION, "Marylebone Station", 2),
    PropertyCard(PropertyColour.BROWN, "Old Kent Road", 1),
    PropertyCard(PropertyColour.BROWN, "Whitechapel Road", 1),
    PropertyCard(PropertyColour.PALEBLUE, "Euston Road", 1),
    PropertyCard(PropertyColour.PALEBLUE, "Pentonville Road", 1),
    PropertyCard(PropertyColour.PALEBLUE, "The Angel, Islington", 1),
    PropertyCard(PropertyColour.ORANGE, "Vine Street", 2),
    PropertyCard(PropertyColour.ORANGE, "Marlborough Street", 2),
    PropertyCard(PropertyColour.ORANGE, "Bow Street", 2),
    PropertyCard(PropertyColour.MAGENTA, "Northumberland Ave", 2),
    PropertyCard(PropertyColour.MAGENTA, "Whitehall", 2),
    PropertyCard(PropertyColour.MAGENTA, "Pall Mall", 2),
    PropertyCard(PropertyColour.YELLOW, "Leicester Square", 3),
    PropertyCard(PropertyColour.YELLOW, "Coventry Street", 3),
    PropertyCard(PropertyColour.YELLOW, "Piccadilly", 3),
    PropertyCard(PropertyColour.RED, "Fleet Street", 3),
    PropertyCard(PropertyColour.RED, "Strand", 3),
    PropertyCard(PropertyColour.RED, "Trafalgar Square", 3),
    PropertyCard(PropertyColour.GREEN, "Bond Street", 4),
    PropertyCard(PropertyColour.GREEN, "Regent Street", 4),
    PropertyCard(PropertyColour.GREEN, "Oxford Street", 4),
    PropertyCard(PropertyColour.DARKBLUE, "Park Lane", 4),
    PropertyCard(PropertyColour.DARKBLUE, "Mayfair", 4),
]

# theres no wildcard for DARKBLUE
PROPERTY_WILDCARDS = [
    WildPropertyCard(PropertyColour.ALL, 0),
    WildPropertyCard(PropertyColour.ALL, 0),
    WildPropertyCard(PropertyColour.DARKBLUE | PropertyColour.GREEN, 4),
    WildPropertyCard(PropertyColour.STATION | PropertyColour.UTILITY, 2),
    WildPropertyCard(PropertyColour.STATION | PropertyColour.PALEBLUE, 4),
    WildPropertyCard(PropertyColour.MAGENTA | PropertyColour.ORANGE, 2),
    WildPropertyCard(PropertyColour.MAGENTA | PropertyColour.ORANGE, 2),
    WildPropertyCard(PropertyColour.RED | PropertyColour.YELLOW, 3),
    WildPropertyCard(PropertyColour.RED | PropertyColour.YELLOW, 3),
    WildPropertyCard(PropertyColour.STATION | PropertyColour.GREEN, 4),
    WildPropertyCard(PropertyColour.PALEBLUE | PropertyColour.BROWN, 1),
]


class RentCard(Card):
    def __init__(self, colours: PropertyColour, cash: int):
        super().__init__(cash, f"RentCard[{colours}]")
        self.colours = colours
        self.all_players = True


class RainbowRentCard(Card):
    def __init__(self, cash: int):
        super().__init__(cash, "RainbowRentCard")
        self.colours = PropertyColour.ALL
        self.all_players = False


RENT_CARDS = [
    *[RentCard(PropertyColour.BROWN | PropertyColour.PALEBLUE, 1) for _ in range(2)],
    *[RentCard(PropertyColour.MAGENTA | PropertyColour.ORANGE, 1) for _ in range(2)],
    *[RentCard(PropertyColour.RED | PropertyColour.YELLOW, 1) for _ in range(2)],
    *[RentCard(PropertyColour.GREEN | PropertyColour.DARKBLUE, 1) for _ in range(2)],
    *[RentCard(PropertyColour.STATION | PropertyColour.UTILITY, 1) for _ in range(2)],
    *[RainbowRentCard(3) for _ in range(3)],
]


class MoneyCard(Card):
    def __init__(self, cash: int):
        super().__init__(cash, f"MoneyCard[{cash}]")


MONEY_DECK = []
for qty, val in (6, 1), (5, 2), (3, 3), (3, 4), (2, 5), (1, 10):
    for i in range(qty):
        MONEY_DECK.append(MoneyCard(val))


class PassGoCard(Card):
    def __init__(self) -> None:
        super().__init__(1, "PassGoCard")


class DoubleTheRentCard(Card):
    def __init__(self) -> None:
        super().__init__(1, "DoubleTheRentCard")


class BirthdayCard(Card):
    def __init__(self) -> None:
        super().__init__(2, "BirthdayCard")


class ForcedDealCard(Card):
    def __init__(self) -> None:
        super().__init__(3, "ForcedDealCard")


class SlyDealCard(Card):
    def __init__(self) -> None:
        super().__init__(3, "SlyDealCard")


class DealBreakerCard(Card):
    def __init__(self) -> None:
        super().__init__(5, "DealBreakerCard")


class DebtCollectorCard(Card):
    def __init__(self) -> None:
        super().__init__(5, "DebtCollectorCard")


class JustSayNoCard(Card):
    def __init__(self) -> None:
        super().__init__(3, "JustSayNoCard")


ACTION_CARDS = [
    *[PassGoCard() for _ in range(10)],
    *[HotelCard() for _ in range(2)],
    *[HouseCard() for _ in range(3)],
    *[DoubleTheRentCard() for _ in range(2)],
    *[BirthdayCard() for _ in range(3)],
    *[ForcedDealCard() for _ in range(3)],
    *[SlyDealCard() for _ in range(3)],
    *[DealBreakerCard() for _ in range(2)],
    *[DebtCollectorCard() for _ in range(3)],
    *[JustSayNoCard() for _ in range(3)],
]

DECK = MONEY_DECK + PROPERTY_DECK + PROPERTY_WILDCARDS + RENT_CARDS + ACTION_CARDS

if __name__ == "__main__":
    for c in DECK:
        print(c)
