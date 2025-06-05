![Python versions](https://img.shields.io/pypi/pyversions/monodeal.svg) ![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/shuckc/monodeal/check.yml) [![PyPI version](https://badge.fury.io/py/monodeal.svg)](https://badge.fury.io/py/monodeal)

Monopoly Deal (card game) simulator in python
=====

Quickstart:

```
% python -m monodeal.game
Player A recieved RentCard[PropertyColour.GREEN|DARKBLUE]
Player B recieved MoneyCard[1]
Player A recieved MoneyCard[1]
Player B recieved PropertyCard[GREEN,'Oxford Street']
Player A recieved MoneyCard[2]
Player B recieved PropertyCard[ORANGE,'Vine Street']
Player A recieved RentCard[PropertyColour.BROWN|PALEBLUE]
...
Player B recieved PropertyCard[STATION,'Liverpool St']
Player B recieved PropertyCard[MAGENTA,'Pall Mall']
Player B has hand [PropertyCard[STATION,'Liverpool St'], PropertyCard[MAGENTA,'Pall Mall']]
Player B has property [
    PS(GREEN,3/3,Oxford Street,Regent Street,Bond Street,-,-), 
    PS(ORANGE,2/3,Vine Street,Bow Street,-,-), 
    PS(STATION,2/4,Fenchurch St,Kings Cross Station,-,-), 
    PS(MAGENTA,2/3,Northumberland Ave,Whitehall,-,-), 
    PS(DARKBLUE,1/2,Mayfair,-,-), 
    PS(PALEBLUE,1/3,Euston Road,-,-), 
    PS(BROWN,2/2,Whitechapel Road,Old Kent Road,-,-), 
    PS(YELLOW,1/3,Leicester Square,-,-), 
    PS(RED,2/3,Strand,Trafalgar Square,-,-), 
    PS(UTILITY,1/2,Electric Company,-,-)])
Player B does action PlayPropertyAction(player=Player B, card=PropertyCard[STATION,'Liverpool St'], colour=<PropertyColour.STATION: 2>)
Player B does action PlayPropertyAction(player=Player B, card=PropertyCard[MAGENTA,'Pall Mall'], colour=<PropertyColour.MAGENTA: 32>)
Player B has won!
```

Open topics:
* best discard and payment strategy to meet hand size or payment demand
    * good insight at https://github.com/johnsears/monopoly-deal/blob/master/src/monopoly_deal/game.py#L227 : any superset of a viable payment set is worse than the original
* optimise wildcards, house and hotels within property sets to maximise `rv` and `cps`
* scoring and ordering actions

Edge Cases
-----
The official rules seem silent on a number of issues:

* If a player without a complete property set recieves a house or hotel as incoming payment, where does the house/hotel card go? There seem to be three resonable choices:
    1) card is placed in the cash pile, and has now lost it's special property-card handling
    1) card can be placed on an incomplete property set, but does not count for rent calculation purposes until completed
    1) card is placed as property, but not in a specific property set. The player can 'allocate' this at a later time to a complete property set
* Can a player move house/hotel cards between property sets? If so, when, and is this an action for the 3-actions rule? If this is allowed, then a player with multiple complete property sets can, with one house and hotel, move them between sets before charging rent. ie. effectively the Player has a house/hotel "globally" for rent optimisation rather than fixing them to a particular property set. This seems at odds with the DealBreaker's action to take a complete property set with any house/hotel cards.
    1) house/hotel can not be moved once played into a property set
    1) house/hotel can be moved to another complete PS, like a wildcard, before any player action.
    1) house/hotel cards can be moved, at the cost of 1 action
* If the deck is exhausted during play, does the discard pile get shuffled to become the new deck?
* Holding 'extra' property of a colour due to wildcards: If we hold all 3 Green PropertyCards, plus a Blue/Green WildPropertyCard played as Green, how is this represented?
    1) one Green Property Sets containing 4 cards, which is 'complete' (for winning purposes) with base rent capped at the maximum value for the colour (ie. the 4th card only contirbutes cash value).
    1) two Green Property Sets, one of 3 cards (complete), one of 1 card (incomplete). The incomplete set is vulnerable to SlyDeal / ForcedDeal actions, and the complete set vulnerable to the DealBreaker action. Rent could be charged on either set (although sub-optimally on the smaller).
    1) two green property sets (as b) however a Green Rent card collects rents for *both* property sets
* Merging of separate propertysets: Per (b) above. If I have a Brown card, and the use DealBreaker to aquire a set of Brown+Wildcard(Brown) from another player, treating these as separate sets. If I then flip the WildPropertyCard from Brown to PaleBlue, can and how do the orphaned two Brown cards get combined?
* Forfeiting Buildings:  The rules (for house and hotel cards) state "If the property set they're on becomes incomplete, discard them". However since houses and hotels are only placed on complete property sets, and complete sets are immune from SlyDeal / ForcedDealCard actions, this could only happen due to:
    1) the decision to settle a debt with a property card from a complete set, In doing this the player pays the cash value of the lost property to the opposition, and forfeits the house/hotel cash value to the discard pile. I can't see this ever being a better strategic option than paying with the house or hotel.
    1) re-allocating a WildPropertyCard to another colour, before replacing it with another matching colour from the hand. (See the point on holding extra property in a set above - as this rule interacts with that).
    1) It seems earlier instructions moved forfeited house/hotel cards to the player's bank rather than the discard pile
* Quadruple rent: Playing two DoubleTheRent cards simultaniously:
    1) allowed: this uses all 3 actions of the player's go, and charges 4x the property set's rent
    1) invalid - only one DTR card may be played on per Rent card

* Use a ForcedDeal to push a card (G) to a player (with GG) to complete a set, so that a DealBreaker can then be played to capture the full set (GGG):
    1) seems fine to me!
* Play a JustSayNo card against a rent claim that has no cost to a player with no property/cash in order to empty the hand so that 5 cards are recieved on the next round.
    1) seems fine to me!

Some of these are from https://boardgamegeek.com/thread/375594/rules-clarification/page/1

Some strategy tips: https://boardgamegeek.com/thread/787900/article/8895582#8895582


Other work
---
* Rules etc https://monopolydealrules.com/index.php?page=cards#top
* deck representation https://github.com/brylee123/MonopolyDeal/blob/master/init_deck.py

Thoughts
----
When a player does an action:
```
    SkipAction

    DepositAction
        card: MoneyCard or ActionCard

    PlayPropertyAction
        card: PropertyCard, WildPropertyCard, HouseCard, HotelCard
        colour: PropertyColour
  
    PlayAction
        card: action card or None
        opponent: player or None
   
    ForcedDeal
        opposing (player, property set, property index)    [not from a complete set]
        your (property set, property index)

    SlyDeal
        opposing (player, property set, property index)    [not from a complete set]

    RentAction
       card: RentCard | RainbowRentCard
       propertyset: PropertySet (with propertyset.colour in card.colour)
       double_rent: DoubleTheRentCard|None
       quad_rent: DoubleTheRentCard|None
       target: PlayerProto | None

    DebtCollector
        card: DebtCollectorCard
        target: PlayerProto

    BirthdayAction
        card: BirthdayCard

    DealBreakerAction
        opposing (player, property set)

    MoveProperty (does not count as one of 3 actions)
        existing propertySet index, property index
        new propertySet index

```