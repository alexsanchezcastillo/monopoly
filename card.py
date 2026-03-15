from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from player import Player
    from board import Board

class Card:
    """Base class for all Monopoly cards."""

    def __init__(self, id: int, title: str, description: str, action: str) -> None:
        self._id = id
        self._title = title
        self._description = description
        self._action = action

    def id(self) -> int:
        return self._id
        
    def title(self) -> str:
        return self._title
        
    def description(self) -> str:
        return self._description
        
    def action(self) -> str:
        return self._action

    def execute(self, player: Player, board: Board) -> None:
        raise NotImplementedError("Subclasses must implement execute().")

class MoneyCard(Card):
    """Handles collect_money and pay_money actions."""
    def __init__(self, id: int, title: str, description: str, action: str, amount: int) -> None:
        super().__init__(id, title, description, action)
        self._amount = amount
        
    def execute(self, player: Player, board: Board) -> None:
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
                    player.transaction(-self._amount_per_player)
                    other.transaction(self._amount_per_player)
                else:
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
    """Factory to build cards from JSON data."""
    c_id, title, desc, action = data.get("id", 0), data.get("title", ""), data.get("description", ""), data.get("action", "")

    if action == "collect_money":
        return MoneyCard(c_id, title, desc, action, data.get("amount", 0))
    elif action == "pay_money":
        return MoneyCard(c_id, title, desc, action, -data.get("amount", 0))
    elif action == "move_to_position":
        return MoveToPositionCard(c_id, title, desc, action, data.get("position", 0))
    elif action == "move_back_spaces":
        return MoveBackSpacesCard(c_id, title, desc, action, data.get("spaces", 0))
    elif action == "go_to_jail":
        return GoToJailCard(c_id, title, desc, action, data.get("position", 10))
    elif action == "get_out_of_jail_card":
        return GetOutOfJailCard(c_id, title, desc, action)
    elif action == "pay_per_property":
        return PropertyRepairsCard(c_id, title, desc, action, data.get("amountPerHouse", 0), data.get("amountPerHotel", 0))
    elif action in ["pay_each_player", "collect_from_players"]:
        return PlayerTransactionCard(c_id, title, desc, action, data.get("amountPerPlayer", 0))
    elif "nearest" in action:
        return MoveNearestCard(c_id, title, desc, action, data.get("rentMultiplier", 1))
    
    return Card(c_id, title, desc, action)