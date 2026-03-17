from __future__ import annotations
from const import START_MONEY, GO_SALARY
from typing import TYPE_CHECKING, Any
from tile import Property, Street
from strategy import Strategy


if TYPE_CHECKING:
    from board import Board

class Player:
    """
    Represents a player in the Monopoly game.
    Manages the player's state, including position, funds, and properties.
    """
    _board: Board
    _name: str
    _color: str
    _index: int
    _position: int
    _money: int
    _in_jail: bool
    _jail_turns: int
    _owned_properties: set[Property]
    _get_out_of_jail_cards: int
    _creditor: Player | None
    

    def __init__(
        self,
        board: Board,
        name: str,
        piece: str,
        color: str,
        index: int,
    ): 
        """Initializes a new player with data from the JSON file."""

        # Attributes loaded from JSON
        self._board = board
        self._name = name
        self._color = color
        self._piece = piece
        self._index = index  
        
        # Dynamic attributes (game state)
        self._position = 0  
        self._money = START_MONEY  
        self._is_in_jail = False
        self._jail_turns = 0
        self._owned_properties = set()
        self._strategy: Strategy = Strategy()
        self._get_out_of_jail_cards = 0
        self._creditor: Player | None = None
    
    def decide_buy(self, property_tile: Property) -> bool:
        """
        Delegates the purchase decision to the player's current strategy.
        """
        return self._strategy.buy_property(self, property_tile)
    
    def strategy(self) -> Strategy:
        """Returns the player's current strategy."""
        return self._strategy

    def move(self, steps: int) -> None:
        """
        Moves the player a specified number of steps across the board.
        If the player passes or lands on the 'GO' tile, they collect the salary.

        Args:
            steps (int): The number of tiles to advance.
        """
        old_position = self._position
        total_tiles = self._board.num_tiles()
        
        # Update position wrapping around the board (modular arithmetic)
        self._position = (self._position + steps) % total_tiles
        
        # Check if the player passed GO 
        if self._position < old_position:
            self._money += GO_SALARY
            print(f"{self._name} passed GO and collected {GO_SALARY}!")

    def move_to(self, position: int) -> None:
        """
        Moves the player directly to a specific position on the board.
        If the player passes or lands on the 'GO' tile, they collect the salary.

        Args:
            position (int): The target tile index to move to.
        """
        old_position = self._position
        total_tiles = self._board.num_tiles()
        
        # Update position directly to the target
        self._position = position % total_tiles
        
        # Check if the player passed GO
        if self._position < old_position:
            self._money += GO_SALARY
            print(f"{self._name} passed GO and collected {GO_SALARY}!")

    def get_color_group_player(self, color: str) -> list[Street]:
        """Returns a list of all streets of a specific color owned by the player."""
        return [street for street in self._owned_properties 
                if isinstance(street, Street) and street.color() == color]

    def board(self) -> Board:
        return self._board

    def name(self) -> str:
        return self._name

    def piece(self) -> str:
        return self._piece

    def color(self) -> str:
        return self._color

    def money(self) -> int:
        return self._money
    
    def total_houses(self) -> int:
        """Returns the total number of houses owned by the player across all properties."""
        return sum(street.num_houses() for street in self._owned_properties 
                   if isinstance(street, Street))
    
    def total_hotels(self) -> int:
        """Returns the total number of hotels owned by the player across all properties."""
        return sum(1 for street in self._owned_properties 
                   if isinstance(street, Street) and street.has_hotel())

    def position(self) -> int:
        return self._position

    def index(self) -> int:
        return self._index

    def broke(self) -> bool:
        """Return True if the player has negative money."""
        return self._money < 0
    
    def go_to_jail(self, jail_position: int) -> None:
        """Sends the player directly to jail without collecting GO salary."""
        self._position = jail_position
        self._is_in_jail = True
        self._jail_turns = 0
    
    def is_in_jail(self) -> bool:
        """Returns True if the player is currently in jail."""
        return self._is_in_jail
    
    def exit_jail(self) -> None:
        """Removes the player from jail."""
        self._is_in_jail = False
        self._jail_turns = 0
    
    def increment_jail_turn(self) -> None:
        """Increments the jail turn counter."""
        if self._is_in_jail:
            self._jail_turns += 1
    
    def get_out_of_jail_free_cards(self) -> int:
        """Returns the number of Get Out of Jail Free cards the player has."""
        return self._get_out_of_jail_cards
    
    def add_get_out_of_jail_card(self) -> None:
        """Adds a 'Get Out of Jail Free' card to the player's inventory."""
        self._get_out_of_jail_cards += 1

    def use_get_out_of_jail_card(self) -> bool:
        """
        Uses a card to leave jail. 
        Returns True if the player had a card and used it, False otherwise.
        """
        if self._get_out_of_jail_cards > 0:
            self._get_out_of_jail_cards -= 1
            self._is_in_jail = False
            self._jail_turns = 0
            return True
        return False

    def turns_in_prison(self) -> int:
        """Returns the number of turns the player has spent in jail."""
        return self._jail_turns if self._is_in_jail else 0

    def owned_properties(self) -> set[Property]:
        return self._owned_properties

    def creditor(self) -> Player | None:
        """Returns the player who this player (self) has to pay, or None if is the bank."""
        return self._creditor

    def set_creditor(self, player: Player | None) -> None:
        """Sets the creditor (the player this player owes rent to)."""
        self._creditor = player
    
    def transaction(self, amount: int) -> None:
        """Adjusts the player's balance by the given amount (positive or negative)."""
        self._money += amount
        return
    
    def buy_property(self, property_tile: Property) -> None:
        """Purchases a property tile: adds it to owned properties, deducts the price, and sets ownership."""
        self._owned_properties.add(property_tile)
        self.transaction(-property_tile.price())
        property_tile.set_owner(self)
        return


def build_player(board: Board, data: dict[str, Any], index: int) -> Player:
    """Build a Player from JSON dictionary with 'name', 'piece', and 'color' keys."""
    return Player(board, data["name"], data["piece"], data["color"], index)
