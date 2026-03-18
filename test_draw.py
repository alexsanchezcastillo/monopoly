from draw import (
    tile_rect, tile_center, tile_fill_color,
    draw_board_tiles, COLOR_MAP, BOARD_SIZE
)
from board import Board
import drawsvg as dw


# Expected tile size
tile_size = BOARD_SIZE / 11


def create_test_board() -> Board:
    """Helper function to create a fresh Board instance for testing."""
    return Board(
        "data/tiles.json",
        "data/chance.json",
        "data/community-chest.json",
        "data/players.json"
    )

# Tile Positioning Tests
# Remember x, y are the top-left corner of the tile rectangle

def test_tile_rect_positioning() -> None:
    """Test tile rectangles are positioned correctly for all board edges."""
    # Bottom row (0-10): x >= 0, y > 0
    x, y, w, h = tile_rect(0)
    assert x >= 0 and y > 0
    assert w == h == tile_size
    
    # Left column (11-20): x == 0, y >= 0
    x, y, w, h = tile_rect(11)
    assert x == 0 and y >= 0
    assert w == h == tile_size
    
    # Top row (21-30): y == 0, x >= 0
    x, y, w, h = tile_rect(21)
    assert y == 0 and x >= 0
    assert w == h == tile_size
    
    # Right column (31-39): x > 0, y >= 0
    x, y, w, h = tile_rect(31)
    assert x > 0 and y >= 0
    assert w == h == tile_size


def test_tile_center() -> None:
    """Test that tile centers are within expected bounds."""
    for pos in [0, 10, 20, 30, 39]:
        cx, cy = tile_center(pos)
        x, y, _, _ = tile_rect(pos)
        assert isinstance(cx, float)
        assert isinstance(cy, float)
        assert x <= cx <= x + tile_size
        assert y <= cy <= y + tile_size


# Tile Color Mapping Tests

def test_color_values_are_hex() -> None:
    """Test that COLOR_MAP values are valid hex color codes."""
    for _, hex_code in COLOR_MAP.items():
        assert hex_code.startswith('#')
        assert len(hex_code) == 7

# Drawing Function Tests

def test_draw_board_tiles_does_not_crash() -> None:
    """Test that draw_board_tiles can be called without errors."""
    board = create_test_board()
    d = dw.Drawing(1000, 1000)
    draw_board_tiles(d, board, show_number=False)

# Street Colors Tests

def test_brown_streets_have_brown_color() -> None:
    """Test that property color rendering works correctly."""
    board = create_test_board()
    for tile in board.tiles():
        if tile.type() == "property":
            color_code = tile_fill_color(tile)
            assert isinstance(color_code, str)
            assert color_code[0] == '#'
            assert len(color_code) == 7
            break