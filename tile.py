from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from board import Board
    from player import Player

class Tile:
    """
    Base class for all board tiles in the Monopoly game.
    Provides fundamental attributes and methods shared across all specific tile types.
    """
    _board: Board
    _position: int
    _name: str
    _tile_type: str
    _description: str

    def __init__(
        self,
        board: Board,
        position: int,
        name: str,
        tile_type: str,
        description: str,
    ):
        """Initializes a Tile object with the following arguments:
        board, position, name, tile_type and description."""
        self._board = board
        self._position = position
        self._name = name
        self._tile_type = tile_type
        self._description = description

    def land_on(self, player: Player) -> None:
        """Handle what happens when a player lands on this tile. By default it does nothing.
        However, for each tile subclass this function is defined as needed."""
        pass

    def type(self) -> str:
        """Returns the type of the tile."""
        return self._tile_type

    def name(self) -> str:
        """Returns the name of the tile."""
        return self._name

    def description(self) -> str:
        """Returns the description of the tile."""
        return self._description

    def position(self) -> int:
        """Returns the position index of the tile on the board."""
        return self._position

    def board(self) -> Board:
        """Returns the board to which the tile belongs."""
        return self._board    
    
    def get_owner(self) -> Player | None:
        """Returns the owner of the tile if it has one, otherwise returns None.
        This method is overridden in property tiles to return the actual owner."""
        return None

class Property(Tile):
    """
    Abstract base class for all purchasable tiles (Streets, Stations, Utilities).
    Manages ownership, purchasing logic, and rent transactions.
    """
    _owner: Player | None
    _price: int
    _mortgage: int
    _is_mortgaged: bool

    def __init__(
        self,
        board: Board,
        position: int,
        name: str,
        tile_type: str,
        description: str,
        price: int,
        mortgage: int,
    ):
        """Initializes a Property object with a price and mortgage value, in addition to the standard Tile attributes."""
        super().__init__(board, position, name, tile_type, description)  # to use the father __init__'s declaration of variables
        self._price = price
        self._mortgage = mortgage
        self._owner = None
        self._is_mortgaged = False

    def land_on(self, player: Player) -> None:
        """
        Handles the event when a player lands on this property.
        If the property is unowned, the player is asked to buy it.
        If it is owned by another player, rent is paid.
        """
        if self._is_mortgaged:
            print(f"{self._name} is mortgaged. No rent is paid!")
            return  # The player doesn't pay anything

        if self._owner is not None and self._owner != player:
            rent_amount = self.get_rent()
            player.set_creditor(self._owner)
            player.transaction(-rent_amount)
            self._owner.transaction(rent_amount)

        elif self._owner is None:
            player.set_creditor(None)
            # We ask the player (who asks their strategy) if they want to buy
            if player.decide_buy(self):   
                player.transaction(-self._price) 
                self._owner = player
                player.owned_properties().add(self)

    def get_rent(self) -> int:  # this method is implemented differently in each subclass
        """Calculates rent. Must be overridden by subclasses."""
        raise NotImplementedError("Subclasses must implement get_rent()")
    
    def get_owner(self) -> Player | None:
        """Returns the current owner of the property, or None if unowned."""
        return self._owner
    
    def price(self) -> int:
        """Returns the purchase price of the property."""
        return self._price
    
    def is_mortgaged(self) -> bool:
        """Returns True if the property is currently mortgaged."""
        return self._is_mortgaged

    def can_mortgage(self) -> bool:
        """Checks if the property can be mortgaged."""
        if self._owner is None or self._is_mortgaged:
            return False
        return True

    def mortgage(self) -> bool:
        """Mortgages the property for half its price."""
        if self.can_mortgage() and self._owner is not None: 
            self._is_mortgaged = True
            mortgage_value = int(self._price / 2)
            self._owner.transaction(mortgage_value)
            print(f"{self._owner.name()} has mortgaged {self._name} for {mortgage_value}!")
            return True
        return False

    def can_unmortgage(self) -> bool:
        """Checks if the property can be unmortgaged (has enough money)."""
        if self._owner is None or not self._is_mortgaged:
            return False
            
        # Unmortgage cost is the mortgage value (price / 2) plus 10% interest
        unmortgage_cost = int((self._price / 2) * 1.1)
        if self._owner.money() < unmortgage_cost:
            return False
        return True

    def unmortgage(self) -> bool:
        """Unmortgages the property paying the mortgage value + 10%."""
        if self.can_unmortgage() and self._owner is not None:
            unmortgage_cost = int((self._price / 2) * 1.1)
            self._owner.transaction(-unmortgage_cost)
            self._is_mortgaged = False
            print(f"{self._owner.name()} has unmortgaged {self._name} for {unmortgage_cost}!")
            return True
        return False
    
    def set_owner(self, player: Player|None) -> None:
        """Sets the owner of the property."""
        self._owner = player

class Street(Property):
    """
    Represents a standard colored street property where houses and hotels can be built.
    """
    _color: str
    _rent: int
    _rent_with_color_set: int
    _rent_with_1_house: int
    _rent_with_2_house: int
    _rent_with_3_house: int
    _rent_with_4_house: int
    _rent_with_hotel: int
    _house_cost: int
    _hotel_cost: int
    _num_houses: int
    _has_hotel: bool

    def __init__(
        self,
        board: Board,
        description: str,
        position: int,
        name: str,
        tile_type: str,
        color: str,
        price: int,
        rent: int,
        rent_with_color_set: int,
        rent_with_1_house: int,
        rent_with_2_houses: int,
        rent_with_3_houses: int,
        rent_with_4_houses: int,
        rent_with_hotel: int,
        house_cost: int,
        hotel_cost: int,
        mortgage: int,
    ):
        """Initializes a Street property with all its specific rent tiers."""
        super().__init__(board, position, name, tile_type, description, price, mortgage)
        self._rent = rent
        self._color = color
        self._rent_with_color_set = rent_with_color_set
        self._rent_with_1_house = rent_with_1_house
        self._rent_with_2_houses = rent_with_2_houses
        self._rent_with_3_houses = rent_with_3_houses
        self._rent_with_4_houses = rent_with_4_houses
        self._rent_with_hotel = rent_with_hotel
        self._house_cost = house_cost
        self._hotel_cost = hotel_cost
        self._num_houses = 0
        self._has_hotel = False
    
    def color(self) -> str:
        """Returns the color of the street."""
        return self._color
    
    def get_rent(self) -> int:
        """Returns the price that a player has to pay if 
        they land on the street at the current stage."""
        # 1. Mortgaged properties charge no rent
        if self.is_mortgaged():
            return 0

        # 2. Hotel provides the maximum rent tier
        if self.has_hotel():
            return self._rent_with_hotel

        # 3. Rents based on the number of houses
        num_houses = self.num_houses()
        if num_houses > 0:
            rents_houses = [
                self._rent_with_1_house, 
                self._rent_with_2_houses, 
                self._rent_with_3_houses, 
                self._rent_with_4_houses
            ]
            return rents_houses[num_houses - 1]

        # 4. No buildings: check if the owner has a color-set monopoly
        base_rent = self._rent
        owner = self.get_owner()
        if owner is not None and self._board.has_monopoly(owner, self.color()):
            return self._rent_with_color_set
        
        return base_rent
    # Houses actions:

    def num_houses(self) -> int:
        """Returns the number of houses built on this street."""
        return self._num_houses
        
    def can_build_house(self, board: Board) -> bool:
        """Checks if a house can be built following the official Monopoly rules."""
        if self._owner is None:
            return False
            
        # 1. Limit of 4 houses
        if self._num_houses >= 4:
            return False
        
        # 2. Check hotel (can't build a house if there's already a hotel)
        if self._has_hotel:
            return False
            
        # 3. Check Monopoly (Player must own all properties of this color)
        total_color_group = board.get_color_group(self._color)
        player_color_group = self._owner.get_color_group_player(self._color)
        
        if len(total_color_group) != len(player_color_group):
            return False 
            
        # 4. Check Uniform Building (Even build rule)
        for street in player_color_group:
            if street.num_houses() < self._num_houses:
                return False
                
        # 5. Check Funds
        if self._owner.money() < self._house_cost:
            return False
            
        return True

    def build_house(self, board: Board) -> bool: 
        """Attempts to build a house. Returns True if successful."""
        if self.can_build_house(board) and self._owner is not None: # ensures we have an owner before trying to charge them
            self._owner.transaction(-self._house_cost)
            self._num_houses += 1
            print(f"{self._owner.name()} has successfully built a house on {self._name}!")
            return True
        return False
    
    def can_sell_house(self) -> bool:
        """Checks if a house can be sold maintaining the uniform building rule."""
        if self._owner is None or self._has_hotel or self._num_houses == 0:
            return False
            
        # Check Uniform Selling
        # No property of the same color can have MORE houses than this one, 
        # and none can have a hotel (hotels must be sold first).
        player_color_group = self._owner.get_color_group_player(self._color)
        for street in player_color_group:
            if street.has_hotel():
                return False
            if street.num_houses() > self._num_houses:
                return False
        return True

    def sell_house(self) -> bool:
        """Sells a house for half its price."""
        if self.can_sell_house() and self._owner is not None:   # ensures we have a house to sell before trying to sell it
            sell_price = int(self._house_cost / 2)
            self._owner.transaction(sell_price)
            self._num_houses -= 1
            print(f"{self._owner.name()} has sold a house on {self._name} for {sell_price}!")
            return True
        return False
    
    # Hotels actions: 
    
    def has_hotel(self) -> bool:
        """Returns True if the street currently has a hotel."""
        return self._has_hotel

    def can_build_hotel(self, board: 'Board') -> bool:
        """Checks if a hotel can be built following the official rules."""
        if self._owner is None:
            return False
            
        # 1. Must have exactly 4 houses and not already have a hotel
        if self._num_houses != 4 or self._has_hotel:
            return False
            
        # 2. Check Uniform Building
        # All properties of this color must have at least 4 houses or a hotel
        player_color_group = self._owner.get_color_group_player(self._color)
        for street in player_color_group:
            if street.num_houses() < 4 and not street.has_hotel():
                return False
                
        # 3. Check Funds
        if self._owner.money() < self._hotel_cost:
            return False
            
        return True

    def build_hotel(self, board: Board) -> bool:
        """Attempts to build a hotel by replacing 4 houses. Returns True if successful."""
        if self.can_build_hotel(board) and self._owner is not None:  # ensures we have an owner before trying to charge them
            self._owner.transaction(-self._hotel_cost)
            self._num_houses = 0 
            self._has_hotel = True
            print(f"{self._owner.name()} has successfully built a hotel on {self._name}!")
            return True
        return False
    
    def can_sell_hotel(self) -> bool:
        """Checks if a hotel can be sold."""
        if not self._has_hotel:
            return False
        return True

    def sell_hotel(self) -> bool:
        """Sells a hotel for half its price and leaves 4 houses on the street."""
        if self.can_sell_hotel() and self._owner is not None:   # ensures we have a hotel to sell before trying to sell it
            sell_price = int(self._hotel_cost / 2)
            self._owner.transaction(sell_price)
            self._has_hotel = False
            self._num_houses = 4
            print(f"{self._owner.name()} has sold a hotel on {self._name} for {sell_price}!")
            return True
        return False
    
    def can_mortgage(self) -> bool:
        """Checks if the street can be mortgaged (must have no houses or hotels)."""
        if self._num_houses > 0 or self._has_hotel:
            return False
        # If it has no buildings, check the standard property rules from the parent class
        return super().can_mortgage()

class Station(Property): 
    """
    Represents a train station property. Rent increases based on 
    how many stations the owner currently possesses.
    """
    _rent_with_1_station: int
    _rent_with_2_stations: int
    _rent_with_3_stations: int
    _rent_with_4_stations: int

    def __init__(
        self,
        board: Board,
        description: str,
        position: int,
        name: str,
        tile_type: str,
        price: int,
        rent_with_1_station: int,
        rent_with_2_stations: int,
        rent_with_3_stations: int,
        rent_with_4_stations: int,
        mortgage: int,
    ):
        """Initializes a Station property with its specific rent tiers."""
        super().__init__(board, position, name, tile_type, description, price, mortgage)
        self._rent_with_1_station = rent_with_1_station
        self._rent_with_2_station = rent_with_2_stations
        self._rent_with_3_station = rent_with_3_stations
        self._rent_with_4_station = rent_with_4_stations

    def get_rent(self) -> int:
        """Calculates rent based on how many stations the owner has."""
        if self._owner is None:
            return 0
        
        # Count how many station tiles the owner currently has
        stations_owned = sum(1 for station in self._owner.owned_properties() if station.type() == "station")

        if stations_owned == 1:
            return self._rent_with_1_station
        elif stations_owned == 2:
            return self._rent_with_2_station
        elif stations_owned == 3:
            return self._rent_with_3_station
        else:
            return self._rent_with_4_station

class Utility(Property): 
    """
    Represents a utility property.
    Rent is calculated by multiplying the current dice roll by a specific multiplier.
    """
    _rent_multiplier: int
    _rent_multiplier_both: int

    def __init__(self,
        board: Board,
        position: int,
        name: str,
        tile_type: str,
        price: int,
        rent_multiplier: int,
        rent_multiplier_both:int,
        description: str,
        mortgage: int,
        ):
        """Initializes a Utility property with its multipliers."""
        super().__init__(board, position, name, tile_type, description, price, mortgage)
        self._rent_multiplier = rent_multiplier
        self._rent_with_both = rent_multiplier_both

    def get_rent(self) -> int:  
        """Returns the price that a player has to pay if 
        they land on the station at the current stage."""
        if self._owner is None:
            return 0
        
        dice1, dice2 = self._board.current_dice()
        total = dice1 + dice2

        utilities_owned = sum(1 for utility in self._owner.owned_properties() if utility.type() == "utility")

        if utilities_owned == 1:
            return total * self._rent_multiplier
        else:
            return total * self._rent_with_both
        
class Tax(Tile): 
    """
    Represents a tax tile (e.g., Income Tax, Luxury Tax).
    Deducts a flat fee from the player who lands on it.
    """
    _tax: int
    def __init__(
            self,
            board: Board,
            position: int,
            name: str,
            tile_type: str,
            description: str,
            amount: int,
    ):
        """Initializes a Tax tile with the specific tax amount."""
        super().__init__(board, position, name, tile_type, description)
        self._tax = amount

    def land_on(self, player: Player) -> None:
        """Deducts the tax amount from the player's money."""
        player.transaction(-self._tax)

class Community_Chest(Tile):
    """Represents a Community Chest tile."""
    def __init__(
        self,
        board: Board,
        position: int,
        name: str,
        tile_type: str,
        description: str,
    ):
        super().__init__(board, position, name, tile_type, description)
    
    def land_on(self, player: Player) -> None:
        """Draws a Community Chest card, executes it, then returns it to the deck."""
        card = self._board.community_chest_deck().draw()
        print(f"{player.name()} draws Community Chest: {card.title()}")
        card.execute(player, self._board)
        self._board.community_chest_deck().add_card(card)

class Chance(Tile):
    """Represents a Chance tile."""
    def __init__(
        self,
        board: Board,
        position: int,
        name: str,
        tile_type: str,
        description: str,
    ):
        super().__init__(board, position, name, tile_type, description)
    
    def land_on(self, player: 'Player') -> None:
        """Draws a Chance card, executes it, then returns it to the deck."""
        card = self._board.chance_deck().draw()
        print(f"{player.name()} draws Chance: {card.title()}")
        card.execute(player, self._board)
        self._board.chance_deck().add_card(card)

class Special(Tile): 
    """Represents special tiles like 'Go', 'Jail', or 'Free Parking'."""
    def __init__(
        self,
        board: Board,
        position: int,
        name: str,
        tile_type: str,
        description: str,
    ):
        super().__init__(board, position, name, tile_type, description)
    
    def land_on(self, player: Player) -> None:
        """Sends the player to jail if this is the 'Go To Jail' tile."""
        if self._name == "Go To Jail":
            player.go_to_jail(10)

def build_tile(board: Board, data: dict[str, Any]) -> Tile:
    """
    Function to construct the appropriate Tile subclass 
    based on the provided dictionary data.

    Args:
        board: The game board instance.
        data: A dictionary containing the tile configuration data.

    Returns:
        An instantiated object of the correct Tile subclass.
    """    
    tile_type = data['type']
    
    position = data["position"]
    name = data["name"]
    description = data.get("description", "")
    
    if tile_type == "property":
        return Street(
            board=board,
            position=position,
            name=name,
            tile_type=tile_type,
            color=data["color"],
            price=data["price"],
            rent=data["rent"],
            rent_with_color_set=data["rentWithColorSet"],
            rent_with_1_house=data["rentWith1House"],
            rent_with_2_houses=data["rentWith2Houses"],
            rent_with_3_houses=data["rentWith3Houses"],
            rent_with_4_houses=data["rentWith4Houses"],
            rent_with_hotel=data["rentWithHotel"],
            house_cost=data["houseCost"],
            hotel_cost=data["hotelCost"],
            mortgage=data["mortgage"],
            description=description
        )
    
    elif tile_type == "station":
        return Station(
            board=board,
            position=position,
            name=name,
            tile_type=tile_type,
            price=data["price"],
            rent_with_1_station=data["rent"],
            rent_with_2_stations=data["rentWith2Stations"],
            rent_with_3_stations=data["rentWith3Stations"],
            rent_with_4_stations=data["rentWith4Stations"],
            mortgage=data["mortgage"],
            description=description
        )

    elif tile_type == "utility":

        return Utility(
            board=board,
            position=position,
            name=name,
            tile_type=tile_type,
            price=data["price"],
            mortgage=data["mortgage"],
            description=description,
            rent_multiplier=data["rentMultiplier"],
            rent_multiplier_both=data["rentMultiplierWithBoth"]
        )

    elif tile_type == "tax":
        return Tax(
            board=board,
            position=position,
            name=name,
            tile_type=tile_type,
            amount=data["amount"], 
            description=description
        )
    
    elif tile_type == "community_chest":
        return Community_Chest(
            board=board,
            position=position,
            name=name,
            tile_type=tile_type,
            description=description
        )
    
    elif tile_type == "chance":
        return Chance(
            board=board,
            position=position,
            name=name,
            tile_type=tile_type,
            description=description
        )
    
    elif tile_type == "special":
        return Special(
            board=board,
            position=position,
            name=name,
            tile_type=tile_type,
            description=description
        )

    else:
        return Special(
            board=board,
            position=position,
            name=name,
            tile_type=tile_type,
            description=description
)