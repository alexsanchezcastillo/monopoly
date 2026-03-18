import board as b
def test_board_data_loading():
    """Test that board data loads correctly from JSON files."""
    board = b.Board("data/tiles.json", "data/chance.json", 
                    "data/community-chest.json", "data/players.json")
    assert isinstance(board.tiles(), list)
    assert len(board.tiles()) > 0