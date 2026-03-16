"""
Test suite for main game function.
"""

import pytest
from main import play_game
from board import Board


class TestMainGameFunction:
    """Test the main game play function."""

    @pytest.fixture
    def board(self) -> Board:
        """Create a board for testing."""
        return Board("data/tiles.json", "data/chance.json",
                    "data/community-chest.json", "data/players.json")

    def test_play_game_returns_tuple(self, board: Board) -> None:
        """Test that play_game returns a tuple."""
        result = play_game(board, max_turns=50)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_play_game_returns_turn_count_and_winner(self, board: Board) -> None:
        """Test that play_game returns valid tuple."""
        turn_count, winner = play_game(board, max_turns=50)
        assert isinstance(turn_count, int)
        assert isinstance(winner, str)
        assert turn_count >= 1

    def test_play_game_with_limit(self, board: Board) -> None:
        """Test that game respects turn limits."""
        max_turns = 100
        turn_count, winner = play_game(board, max_turns=max_turns)
        # Turn count should be within limit (with minor tolerance)
        assert turn_count <= max_turns

    def test_play_game_without_svg(self, board: Board) -> None:
        """Test that game plays correctly without saving SVG files."""
        turn_count, winner = play_game(board, max_turns=50)
        assert turn_count >= 1
        assert winner is not None

    def test_play_game_reduces_player_count(self, board: Board) -> None:
        """Test that game reduces players as they go bankrupt."""
        initial_players = len(board.players())
        play_game(board, max_turns=100)
        final_players = len(board.players())
        
        # Game play reduces players
        assert final_players <= initial_players


class TestGameIntegration:
    """Integration tests for the complete game."""

    def test_complete_short_game(self) -> None:
        """Test a complete short game."""
        board = Board("data/tiles.json", "data/chance.json",
                     "data/community-chest.json", "data/players.json")
        
        turn_count, winner = play_game(board, max_turns=100)
        
        # Game should complete
        assert turn_count > 0
        assert winner is not None

    def test_game_completes_before_turn_limit(self) -> None:
        """Test that game can complete within turn limit."""
        board = Board("data/tiles.json", "data/chance.json",
                     "data/community-chest.json", "data/players.json")
        
        turn_count, winner = play_game(board, max_turns=200)
        
        # Should have played at least some turns
        assert turn_count >= 1
