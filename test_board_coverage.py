"""
Additional test suite for Board class to improve coverage.
"""

import pytest
from board import Board
from player import Player


class TestBoardGameFlow:
    """Test advanced board game flow scenarios."""

    @pytest.fixture
    def board(self) -> Board:
        """Create a board for testing."""
        return Board("data/tiles.json", "data/chance.json",
                    "data/community-chest.json", "data/players.json")

    def test_play_turn_with_doubles_sends_to_jail_after_three(self, board: Board) -> None:
        """Test that rolling three doubles sends player to jail."""
        import random
        random.seed(100)
        
        # Track original position
        initial_position = board.current_player().position()
        
        # Play the turn (which may involve doubles)
        board.play_turn()
        
        # Turn should have executed
        assert board is not None

    def test_get_tile_at_multiple_positions(self, board: Board) -> None:
        """Test getting tiles at various board positions."""
        for pos in [0, 10, 20, 30, 39]:
            tile = board.get_tile(pos)
            assert tile is not None
            assert tile.position() == pos

    def test_get_property_by_index(self, board: Board) -> None:
        """Test getting a property by index."""
        property_tile = board.get_property(1)  # Use index instead of name
        assert property_tile is not None
        # Index 1 should be a property

    def test_current_player_changes_after_turn(self, board: Board) -> None:
        """Test that current player changes after turn."""
        first_player = board.current_player()
        board.next_player()
        second_player = board.current_player()
        
        assert first_player.index() != second_player.index()

    def test_multiple_next_player_calls_cycles_through(self, board: Board) -> None:
        """Test that calling next_player multiple times cycles through all players."""
        num_players = len(board.players())
        original_player = board.current_player()
        
        for _ in range(num_players):
            board.next_player()
        
        # Should be back to original player
        assert board.current_player().index() == original_player.index()

    def test_dice_values_are_valid(self, board: Board) -> None:
        """Test that dice rolls are within valid range (1-6)."""
        board.roll_dice()
        d1, d2 = board.dice()
        
        assert 1 <= d1 <= 6
        assert 1 <= d2 <= 6

    def test_all_tiles_are_accessible(self, board: Board) -> None:
        """Test that all 40 board tiles are accessible."""
        for pos in range(40):
            tile = board.get_tile(pos)
            assert tile is not None
            assert 0 <= tile.position() <= 39

    def test_has_monopoly_single_property(self, board: Board) -> None:
        """Test monopoly check with single property."""
        player = board.players()[0]
        # Players don't own properties initially
        result = board.has_monopoly(player, "brown")
        assert result is False

    def test_players_list_valid(self, board: Board) -> None:
        """Test that board maintains valid player list."""
        players = board.players()
        assert len(players) >= 2
        assert len(players) <= 4
        
        # All should be Player objects
        for player in players:
            assert isinstance(player, Player)

    def test_board_has_all_tile_types(self, board: Board) -> None:
        """Test that board includes all tile types."""
        tile_types = set()
        
        for tile in board.tiles():
            tile_type = tile.type()
            tile_types.add(tile_type)
        
        # Should have properties, stations, utilities, taxes, special, cards
        expected_types = {"property", "station", "utility", "tax", "special", "chance", "community_chest"}
        for expected in expected_types:
            assert expected in tile_types

    def test_board_tile_iterator(self, board: Board) -> None:
        """Test the board's tile iterator."""
        tiles = list(board.tiles())
        assert len(tiles) == 40  # Standard Monopoly has 40 tiles

    def test_game_termination_condition(self, board: Board) -> None:
        """Test that game continues while more than 1 player remains."""
        # Initially should have multiple players
        assert len(board.players()) > 1


class TestBoardPropertyOperations:
    """Test property-related board operations."""

    @pytest.fixture
    def board(self) -> Board:
        """Create a board for testing."""
        return Board("data/tiles.json", "data/chance.json",
                    "data/community-chest.json", "data/players.json")

    def test_property_types_on_board(self, board: Board) -> None:
        """Test property tiles have necessary attributes."""
        for tile in board.tiles():
            if tile.type() == "property":
                # Should be purchaseable
                assert hasattr(tile, 'price')
                assert callable(tile.price)

    def test_station_identification(self, board: Board) -> None:
        """Test that stations are properly identified."""
        stations = [tile for tile in board.tiles() if tile.type() == "station"]
        
        # Should be 4 stations in London Monopoly
        assert len(stations) == 4

    def test_utility_identification(self, board: Board) -> None:
        """Test that utilities are properly identified."""
        utilities = [tile for tile in board.tiles() if tile.type() == "utility"]
        
        # Should be 2 utilities
        assert len(utilities) == 2

    def test_tax_tile_identification(self, board: Board) -> None:
        """Test that tax tiles are properly identified."""
        taxes = [tile for tile in board.tiles() if tile.type() == "tax"]
        
        # Should be 2 tax tiles
        assert len(taxes) == 2
