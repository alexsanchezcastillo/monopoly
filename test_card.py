"""
Additional test suite for Card classes to improve coverage.
"""

import pytest
from board import Board
from card import build_card


class TestCardFactory:
    """Test the build_card factory function."""

    def test_build_money_card_collect(self) -> None:
        """Test building a collect money card."""
        data: dict[str, int|str] = {"id": 1, "title": "Collect", "description": "Collect £100", 
                "action": "collect_money", "amount": 100}
        card = build_card(data)
        assert card.title() == "Collect"
        assert card.id() == 1

    def test_build_money_card_pay(self) -> None:
        """Test building a pay money card."""
        data: dict[str, int|str] = {"id": 2, "title": "Pay", "description": "Pay £50", 
                "action": "pay_money", "amount": 50}
        card = build_card(data)
        assert card.title() == "Pay"

    def test_build_move_to_position_card(self) -> None:
        """Test building a move to position card."""
        data: dict[str, int|str] = {"id": 3, "title": "Move to GO", "description": "Advance to GO", 
                "action": "move_to_position", "position": 0}
        card = build_card(data)
        assert card.title() == "Move to GO"

    def test_build_go_to_jail_card(self) -> None:
        """Test building a go to jail card."""
        data: dict[str, int|str] = {"id": 4, "title": "Go to Jail", "description": "Go directly to Jail", 
                "action": "go_to_jail", "position": 10}
        card = build_card(data)
        assert card.title() == "Go to Jail"

    def test_build_get_out_of_jail_card(self) -> None:
        """Test building a get out of jail card."""
        data: dict[str, int|str] = {"id": 5, "title": "Get Out of Jail", "description": "Get Out of Jail Free", 
                "action": "get_out_of_jail_card"}
        card = build_card(data)
        assert card.title() == "Get Out of Jail"

    def test_build_property_repairs_card(self) -> None:
        """Test building a property repairs card."""
        data: dict[str, int|str] = {"id": 6, "title": "Repairs", "description": "Pay for repairs",
                "action": "pay_per_property", "amountPerHouse": 25, "amountPerHotel": 100}
        card = build_card(data)
        assert card.title() == "Repairs"

    def test_build_nearest_station_card(self) -> None:
        """Test building a move to nearest station card."""
        data: dict[str, int|str] = {"id": 7, "title": "Station", "description": "Nearest Station",
                "action": "move_to_nearest_station", "rentMultiplier": 2}
        card = build_card(data)
        assert card.title() == "Station"


class TestCardExecution:
    """Test card execution in game context."""

    @pytest.fixture
    def board(self) -> Board:
        """Create a board for testing."""
        return Board("data/tiles.json", "data/chance.json",
                    "data/community-chest.json", "data/players.json")

    def test_money_card_collect_executes(self, board: Board) -> None:
        """Test that money card collection executes."""
        player = board.players()[0]
        initial_money = player.money()
        
        data: dict[str, int|str] = {"id": 1, "title": "Collect", "description": "Collect £100",
                "action": "collect_money", "amount": 100}
        card = build_card(data)
        card.execute(player, board)
        
        assert player.money() == initial_money + 100

    def test_money_card_pay_executes(self, board: Board) -> None:
        """Test that money card payment executes."""
        player = board.players()[0]
        initial_money = player.money()
        
        data: dict[str, int|str] = {"id": 2, "title": "Pay", "description": "Pay £50",
                "action": "pay_money", "amount": 50}
        card = build_card(data)
        card.execute(player, board)
        
        assert player.money() == initial_money - 50

    def test_move_card_executes(self, board: Board) -> None:
        """Test that move card executes."""
        player = board.players()[0]
        
        data: dict[str, int|str] = {"id": 3, "title": "Move", "description": "Move to position 10",
                "action": "move_to_position", "position": 10}
        card = build_card(data)
        card.execute(player, board)
        
        assert player.position() == 10

    def test_jail_card_executes(self, board: Board) -> None:
        """Test that jail card executes."""
        player = board.players()[0]
        
        data: dict[str, int|str] = {"id": 4, "title": "Jail", "description": "Go to Jail",
                "action": "go_to_jail", "position": 10}
        card = build_card(data)
        card.execute(player, board)
        
        assert player.is_in_jail()


class TestCardIntegration:
    """Test card integration with deck and board."""

    def test_cards_can_be_built_from_dict(self) -> None:
        """Test that cards can be built from dictionary data."""
        test_data: list[dict[str, str|int]]  = [
            {"id": 1, "title": "Test", "description": "Test", "action": "collect_money", "amount": 50},
            {"id": 2, "title": "Test", "description": "Test", "action": "move_to_position", "position": 20},
        ]
        
        for data in test_data:
            card = build_card(data)
            assert card is not None
            assert hasattr(card, 'execute')
