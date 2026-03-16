import pytest
from typing import Any
from board import Board, save_board, load_board
from tile import Tile, Property
from player import Player

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
    """Tests if get_tile handles indices larger than 39 correctly using modulo."""
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
    filepath = "test_dummy_board.pkl"

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

def test_play_turn_normal() -> None:
    """Tests a normal turn without doubles."""
    board = create_test_board()
    player = board.current_player()
    initial_pos = player.position()
    
    # We replace the random dice with a function that always returns 3 and 4
    board.roll_dice = lambda: (3, 4)    # type: ignore
    
    # Mock the chance deck to return a card that does nothing
    from card import Card
    
    class NullCard(Card):
        """A card that does nothing when executed."""
        def execute(self, player: Any, board: Any) -> None:
            pass  # Do nothing
    
    null_card = NullCard(999, "No Action", "No action", "no_action")
    board.chance_deck().draw = lambda: null_card  # type: ignore
    board.chance_deck().add_card = lambda x: None  # type: ignore
    
    board.play_turn()
    
    # The player should move exactly 7 steps (without being moved by a card)
    expected_pos = (initial_pos + 7) % board.num_tiles()
    assert player.position() == expected_pos
    
    # The turn must pass to the next player
    assert board.current_player() != player


def test_play_turn_one_double() -> None:
    """Tests a turn with one double roll followed by a normal roll."""
    board = create_test_board()
    player = board.current_player()
    initial_pos = player.position()
    
    # We create a list of rigged rolls
    rolls = [(2, 2), (1, 3)]
    
    # This fake function returns the first item of the list and removes it
    def fake_roll():
        return rolls.pop(0)
    
    board.roll_dice = fake_roll # type: ignore
    board.play_turn()
    
    # The player should move 4 + 4 = 8 steps in total
    expected_pos = (initial_pos + 8) % board.num_tiles()
    assert player.position() == expected_pos
    
    # The turn must pass to the next player
    assert board.current_player() != player


def test_play_turn_three_doubles_jail() -> None:
    """Tests if rolling three consecutive doubles sends the player to jail."""
    board = create_test_board()
    player = board.current_player()
    
    # We replace the random dice to ALWAYS roll doubles (5 and 5)
    board.roll_dice = lambda: (5, 5)    # type: ignore
    
    board.play_turn()
    
    # The player must end up exactly at the jail position
    assert player.position() == board.jail_position()
    
    # The turn must pass immediately
    assert board.current_player() != player


def test_current_player_changes_after_next() -> None:
    """Tests that current player changes after calling next_player."""
    board = create_test_board()
    first_player = board.current_player()
    board.next_player()
    second_player = board.current_player()
    assert first_player.index() != second_player.index()


def test_next_player_cycles_through_all() -> None:
    """Tests that calling next_player cycles back to the original player."""
    board = create_test_board()
    num_players = len(board.players())
    original_player = board.current_player()
    for _ in range(num_players):
        board.next_player()
    assert board.current_player().index() == original_player.index()


def test_all_tiles_are_accessible() -> None:
    """Tests that all 40 board tiles are accessible."""
    board = create_test_board()
    for pos in range(40):
        tile = board.get_tile(pos)
        assert tile is not None
        assert 0 <= tile.position() <= 39


def test_has_monopoly_without_properties() -> None:
    """Tests monopoly check when the player owns nothing."""
    board = create_test_board()
    player = board.players()[0]
    assert board.has_monopoly(player, "brown") is False


def test_players_list_valid() -> None:
    """Tests that board maintains a valid player list."""
    board = create_test_board()
    players = board.players()
    assert 2 <= len(players) <= 4
    for player in players:
        assert isinstance(player, Player)


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


def test_utility_count() -> None:
    """Tests that there are exactly 2 utilities on the board."""
    board = create_test_board()
    utilities = [t for t in board.tiles() if t.type() == "utility"]
    assert len(utilities) == 2


def test_tax_count() -> None:
    """Tests that there are exactly 2 tax tiles on the board."""
    board = create_test_board()
    taxes = [t for t in board.tiles() if t.type() == "tax"]
    assert len(taxes) == 2