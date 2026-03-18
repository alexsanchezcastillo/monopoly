from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from player import Player
    from board import Board

class Card:
    """Base class for all Monopoly cards."""

    def __init__(self, id: int, title: str, description: str, action: str) -> None:
        """Initializes a card with its basic attributes: id, title, description and action."""
        self._id = id
        self._title = title
        self._description = description
        self._action = action

    def id(self) -> int:
        """Returns the unique identifier of the card."""
        return self._id
        
    def title(self) -> str:
        """Returns the title of the card."""
        return self._title
        
    def description(self) -> str:
        """Returns the description of the card."""
        return self._description
        
    def action(self) -> str:
        """Returns the action type of the card, which determines its effect when drawn."""
        return self._action

    def execute(self, player: Player, board: Board) -> None:
        """Executes the card's effect on the given player and board. Must be overridden by subclasses."""
        raise NotImplementedError("Subclasses must implement execute().")

class MoneyCard(Card):
    """Handles collect_money and pay_money actions."""
    def __init__(self, id: int, title: str, description: str, action: str, amount: int) -> None:
        super().__init__(id, title, description, action)
        self._amount = amount
        
    def execute(self, player: Player, board: Board) -> None:
        if self._amount < 0:  # Payment to bank
            player.set_creditor(None)
        player.transaction(self._amount)

class MoveToPositionCard(Card):
    """Handles move_to_position actions."""
    def __init__(self, id: int, title: str, description: str, action: str, position: int) -> None:
        super().__init__(id, title, description, action)
        self._position = position
        
    def execute(self, player: Player, board: Board) -> None:
        player.move_to(self._position)

class MoveBackSpacesCard(Card):
    """Handles move_back_spaces actions."""
    def __init__(self, id: int, title: str, description: str, action: str, spaces: int) -> None:
        super().__init__(id, title, description, action)
        self._spaces = spaces
        
    def execute(self, player: Player, board: Board) -> None:
        player.move(-self._spaces)

class GoToJailCard(Card):
    """Handles go_to_jail actions using the position from JSON."""
    def __init__(self, id: int, title: str, description: str, action: str, position: int) -> None:
        super().__init__(id, title, description, action)
        self._jail_position = position
        
    def execute(self, player: Player, board: Board) -> None:
        player.go_to_jail(self._jail_position)

class GetOutOfJailCard(Card):
    """Handles get_out_of_jail_card actions."""
    def execute(self, player: Player, board: Board) -> None:
        player.add_get_out_of_jail_card()

class PropertyRepairsCard(Card):
    """Handles pay_per_property actions."""
    def __init__(self, id: int, title: str, description: str, action: str, house_cost: int, hotel_cost: int) -> None:
        super().__init__(id, title, description, action)
        self._house_cost = house_cost
        self._hotel_cost = hotel_cost
        
    def execute(self, player: Player, board: Board) -> None:
        cost = (player.total_houses() * self._house_cost) + (player.total_hotels() * self._hotel_cost)
        player.set_creditor(None)  # Payment to bank for repairs
        player.transaction(-cost)

class PlayerTransactionCard(Card):
    """Handles pay_each_player and collect_from_players actions."""
    def __init__(self, id: int, title: str, description: str, action: str, amount_per_player: int) -> None:
        super().__init__(id, title, description, action)
        self._amount_per_player = amount_per_player
        
    def execute(self, player: Player, board: Board) -> None:
        for other in board.players():
            if other != player:
                if self._action == "pay_each_player":
                    player.set_creditor(None)  # Payment to multiple players = bank default
                    player.transaction(-self._amount_per_player)
                    other.transaction(self._amount_per_player)
                else:
                    other.set_creditor(None)  # Payment from multiple players = bank default
                    other.transaction(-self._amount_per_player)
                    player.transaction(self._amount_per_player)

class MoveNearestCard(Card):
    """Handles move_to_nearest_station and move_to_nearest_utility."""
    def __init__(self, id: int, title: str, description: str, action: str, multiplier: int) -> None:
        super().__init__(id, title, description, action)
        self._multiplier = multiplier
        
    def execute(self, player: Player, board: Board) -> None:
        if "station" in self._action:
            board.move_to_nearest_station(player, self._multiplier)
        else:
            board.move_to_nearest_utility(player, self._multiplier)

def build_card(data: dict[str, Any]) -> Card:
    """Builds and returns the appropriate Card subclass from the given JSON data dict."""
    c_id, title, desc, action = data["id"], data["title"], data["description"], data["action"]

    if action == "collect_money":
        return MoneyCard(c_id, title, desc, action, data["amount"])
    elif action == "pay_money":
        return MoneyCard(c_id, title, desc, action, -data["amount"])
    elif action == "move_to_position":
        return MoveToPositionCard(c_id, title, desc, action, data["position"])
    elif action == "move_back_spaces":
        return MoveBackSpacesCard(c_id, title, desc, action, data["spaces"])
    elif action == "go_to_jail":
        return GoToJailCard(c_id, title, desc, action, data["position"])
    elif action == "get_out_of_jail_card":
        return GetOutOfJailCard(c_id, title, desc, action)
    elif action == "pay_per_property":
        return PropertyRepairsCard(c_id, title, desc, action, data["amountPerHouse"], data["amountPerHotel"])
    elif action in ["pay_each_player", "collect_from_players"]:
        return PlayerTransactionCard(c_id, title, desc, action, data["amountPerPlayer"])
    elif "nearest" in action:
        return MoveNearestCard(c_id, title, desc, action, data["rentMultiplier"])
    
    return Card(c_id, title, desc, action)