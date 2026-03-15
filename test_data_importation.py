"""Test for basic data importation from JSON files."""

import board as b
from pathlib import Path

# Resolve the directory where this test file is located
BASE_DIR = Path(__file__).resolve().parent

# Build paths to the data files
tiles_json_path = str(BASE_DIR / "data" / "tiles.json")
chance_json_path = str(BASE_DIR / "data" / "chance.json")
community_chest_json_path = str(BASE_DIR / "data" / "community-chest.json")
players_json_path = str(BASE_DIR / "data" / "players.json")

taulell = b.Board(tiles_json_path, chance_json_path, community_chest_json_path, players_json_path)

def test_board():
    assert isinstance(taulell.tiles(), list)

