import pytest
from typing import Any
from board import Board, save_board, load_board
from tile import Tile, Property
from card import Card

def create_test_board() -> Board:
    """
    Helper function to create a fresh Board instance for testing.
    It uses simple relative paths to the JSON files.
    """
    return Board(
        "data/tiles.json",
        "data/chance.json",
        "data/community-chest.json",
        "data/players.json"
    )

def test_board_initialization() -> None:
    """Tests if the board correctly loads tiles and players."""
    board = create_test_board()
    
    assert board.num_tiles() == 40
    assert len(board.players()) > 0
    assert isinstance(board.tiles()[0], Tile)
    assert board.jail_position() == 10
    assert board.current_player() == board.get_player(0)

def test_roll_dice() -> None:
    """Tests if roll_dice returns valid values between 1 and 6."""
    board = create_test_board()
    
    d1, d2 = board.roll_dice()
    
    assert 1 <= d1 <= 6
    assert 1 <= d2 <= 6
    assert board.current_dice() == (d1, d2)

def test_get_tile_wrap_around() -> None:
    """Tests if get_tile handles indices larger than 39 correctly."""
    board = create_test_board()
    
    tile_0 = board.get_tile(0)
    tile_40 = board.get_tile(40)
    tile_41 = board.get_tile(41)
    
    assert tile_0 == tile_40
    assert board.get_tile(1) == tile_41

def test_save_and_load_board() -> None:
    """Tests the pickle serialization and deserialization functions."""
    board = create_test_board()
    
    # Change a state to verify it saves correctly
    board.roll_dice()
    current_dice_state = board.current_dice()
    
    # We use a simple hardcoded filename for the test
    filepath = "test_board.pkl"

    # Save and Load
    save_board(board, filepath)
    loaded_board = load_board(filepath)
    
    # Verify the loaded object matches the original
    assert loaded_board.num_tiles() == board.num_tiles()
    assert loaded_board.current_dice() == current_dice_state

def test_get_property_success_and_exception() -> None:
    """
    Tests if get_property returns a Property object for valid indices,
    and raises an AttributeError for non-property tiles.
    """
    board = create_test_board()
    
    # Tile 1 (Mediterranean Avenue) is a Property
    prop = board.get_property(1)
    assert isinstance(prop, Property)
    
    # Tile 0 (GO) is not a Property. We expect an AttributeError.
    with pytest.raises(AttributeError):
        board.get_property(0)


def test_next_player_cycles_through_all() -> None:
    """Tests that calling next_player cycles back to the original player."""
    board = create_test_board()
    num_players = len(board.players())
    original_player = board.current_player()
    for _ in range(num_players):
        board.next_player()
    assert board.current_player().index() == original_player.index()


def test_board_has_all_tile_types() -> None:
    """Tests that the board includes all expected tile types."""
    board = create_test_board()
    tile_types = {tile.type() for tile in board.tiles()}
    expected_types = {"property", "station", "utility", "tax", "special", "chance", "community_chest"}
    for expected in expected_types:
        assert expected in tile_types


def test_station_count() -> None:
    """Tests that there are exactly 4 stations on the board."""
    board = create_test_board()
    stations = [t for t in board.tiles() if t.type() == "station"]
    assert len(stations) == 4
