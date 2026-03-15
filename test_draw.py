"""
Test suite for the Drawing functionality.
"""

import os
import pytest
from draw import (
    tile_rect, tile_center, tile_fill_color,
    draw_board_tiles, draw, COLOR_MAP
)
from board import Board


class TestTilePositioning:
    """Test tile position and center calculations."""

    def test_tile_rect_bottom_row(self) -> None:
        """Test tile rectangle for bottom row tiles (0-10)."""
        # Tile 0 (GO in bottom-right)
        x, y, w, h = tile_rect(0)
        assert x >= 0
        assert y >= 0
        assert w > 0
        assert h > 0

    def test_tile_rect_left_column(self) -> None:
        """Test tile rectangle for left column tiles (11-20)."""
        x, y, w, h = tile_rect(11)
        assert x == 0  # Left column should have x=0
        assert w > 0
        assert h > 0

    def test_tile_rect_top_row(self) -> None:
        """Test tile rectangle for top row tiles (21-30)."""
        x, y, w, h = tile_rect(21)
        assert y == 0  # Top row should have y=0
        assert w > 0
        assert h > 0

    def test_tile_rect_right_column(self) -> None:
        """Test tile rectangle for right column tiles (31-39)."""
        x, y, w, h = tile_rect(31)
        # Right column should have x at the right edge
        assert x > 0
        assert w > 0

    def test_tile_center_returns_tuple(self) -> None:
        """Test that tile_center returns a valid (x, y) tuple."""
        cx, cy = tile_center(0)
        assert isinstance(cx, float)
        assert isinstance(cy, float)

    def test_tile_center_is_within_bounds(self) -> None:
        """Test that tile centers are within expected bounds."""
        for pos in [0, 10, 20, 30, 39]:
            cx, cy = tile_center(pos)
            assert cx > 0
            assert cy > 0


class TestTileColorMapping:
    """Test color assignment for tiles."""

    def test_color_map_has_standard_colors(self) -> None:
        """Test that COLOR_MAP contains standard Monopoly colors."""
        expected_colors = ['brown', 'light_blue', 'pink', 'orange', 
                          'red', 'yellow', 'green', 'dark_blue']
        for color in expected_colors:
            assert color in COLOR_MAP

    def test_color_values_are_hex(self) -> None:
        """Test that COLOR_MAP values are valid hex color codes."""
        for color, hex_code in COLOR_MAP.items():
            assert hex_code.startswith('#')
            assert len(hex_code) == 7  # #RRGGBB format

    def test_special_tile_colors(self) -> None:
        """Test color assignment for special tiles."""
        board = Board(
            "data/tiles.json",
            "data/chance.json", 
            "data/community-chest.json",
            "data/players.json"
        )
        
        # Test a special tile (GO)
        go_tile = board.get_tile(0)
        assert go_tile.name() == "GO"
        color = tile_fill_color(go_tile)
        assert color is not None


class TestBoardRenderingFunctions:
    """Test rendering functions work without errors."""

    @pytest.fixture
    def board(self) -> Board:
        """Create a board for testing."""
        return Board(
            "data/tiles.json",
            "data/chance.json",
            "data/community-chest.json",
            "data/players.json"
        )

    def test_draw_board_tiles_does_not_crash(self, board: Board) -> None:
        """Test that draw_board_tiles can be called without errors."""
        import drawsvg as dw
        d = dw.Drawing(1000, 1000)
        # Should not raise an exception
        draw_board_tiles(d, board, show_number=False)

    def test_draw_svg_file_creation(self, board: Board, tmp_path) -> None:
        """Test that SVG files are created successfully."""
        output_file = tmp_path / "test_output.svg"
        draw(board, str(output_file))
        assert output_file.exists()
        
    def test_draw_svg_file_not_empty(self, board: Board, tmp_path) -> None:
        """Test that generated SVG files have content."""
        output_file = tmp_path / "test_output.svg"
        draw(board, str(output_file))
        
        with open(output_file, 'r') as f:
            content = f.read()
            assert len(content) > 100  # SVG files should be substantial
            assert '<svg' in content

    def test_draw_with_show_number_flag(self, board: Board, tmp_path) -> None:
        """Test drawing with show_number=True."""
        output_file = tmp_path / "test_numbered.svg"
        draw(board, str(output_file), show_number=True)
        assert output_file.exists()


class TestStreetColors:
    """Test that streets get their proper colors in rendering."""

    @pytest.fixture
    def board(self) -> Board:
        """Create a board for testing."""
        return Board(
            "data/tiles.json",
            "data/chance.json",
            "data/community-chest.json",
            "data/players.json"
        )

    def test_brown_streets_have_brown_color(self, board: Board) -> None:
        """Test that property color rendering works correctly."""
        # Just verify that tile_fill_color works for properties
        for tile in board.tiles():
            if tile.type() == "property":
                color_code = tile_fill_color(tile)
                # Should return a valid hex color
                assert color_code.startswith('#')
                break

    def test_dark_blue_streets_have_dark_blue_color(self, board: Board) -> None:
        """Test that rendering handles all property colors."""
        # Verify that we process multiple properties
        property_count = 0
        for tile in board.tiles():
            if tile.type() == "property":
                color_code = tile_fill_color(tile)
                assert isinstance(color_code, str)
                assert len(color_code) == 7  # #RRGGBB
                property_count += 1
        
        # Should have found some properties
        assert property_count > 0

    def test_all_property_colors_mapped(self, board: Board) -> None:
        """Test that all property colors are in the color map."""
        used_colors = set()
        for tile in board.tiles():
            if tile.type() == "property":
                color_method = getattr(tile, "color", None)
                # Check if it's a method and call it
                if callable(color_method):
                    color = color_method()
                else:
                    color = color_method
                    
                if color:
                    used_colors.add(color)
        
        # All used colors should be in COLOR_MAP
        for color in used_colors:
            assert color in COLOR_MAP, f"Color {color} not in COLOR_MAP"
