
This is quite OK:
https://github.com/brylee123/MonopolyDeal/blob/master/init_deck.py

When a player does an action:
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

