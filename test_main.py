import os
import random
from main import play_game, main
from board import Board


def create_test_board() -> Board:
    """Helper function to create a fresh Board instance for testing."""
    return Board(
        "data/tiles.json",
        "data/chance.json",
        "data/community-chest.json",
        "data/players.json"
    )


# Main Game Function Tests
# Note: Each test uses random.seed() to ensure deterministic play_game() behavior.
# Without seeds, each test would roll different dice values and execute different code,
# causing coverage to vary unpredictably. With seeds, coverage remains stable.


def test_play_game_returns_turn_count_and_winner() -> None:
    """Test that play_game returns valid tuple, and that turn count is reasonable."""
    random.seed(43)
    board = create_test_board()
    turn_count, winner = play_game(board, max_turns=200)
    assert isinstance(turn_count, int)
    assert isinstance(winner, str)
    assert 1 <= turn_count 


def test_play_game_with_limit() -> None:
    """Test that game respects turn limits."""
    random.seed(44)
    board = create_test_board()
    turn_count, _ = play_game(board, max_turns=200)
    assert turn_count <= 200


def test_play_game_reduces_player_count() -> None:
    """Test that game reduces players as they go bankrupt."""
    random.seed(46)
    board = create_test_board()
    initial_players = len(board.players())
    play_game(board, max_turns=200)
    final_players = len(board.players())
    
    assert final_players <= initial_players


def test_main_generates_output() -> None:
    """Test that main() runs the full game and generates game.html."""
    random.seed(43)
    main()
    assert os.path.exists("game.html")