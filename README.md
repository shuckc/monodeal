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
* optimise wildcards within property sets
* scoring and ordering actions


Other work
---
This is quite OK:
https://github.com/brylee123/MonopolyDeal/blob/master/init_deck.py

Thoughts
----
When a player does an action:
```
    SkipAction

    PlayMoney(MoneyCard or ActionCard)


    PlayProperty(PropertyCard or WildPropertyCard or RainbowPropertyCard)
        existing propertySet or new
  
    MoveProperty (does not count as one of 3 actions)
        existing propertySet index, property index
        new propertySet index
  
    PlayAction
        card: action card or None
        opponent: player or None
   
    ForcedDeal
        opposing (player, property set, property index)    [not from a complete set]
        your (property set, property index)
    SlyDeal
        opposing (player, property set, property index)    [not from a complete set]
   
    HouseAction
        property set that is complete
    
    HotelAction
        property set complete with house
   
    CollectRainbowRent
      opposing player
      your property set

    CollectRent
       RentCard
       your property set (must match one of two flags on card)

    DebtCollector
    	opposing player

    ItsMyBirthdayAction
        card

    DealBreakerAction
        opposing (player, property set)

    JustSayNo action happens ad-hoc?
```