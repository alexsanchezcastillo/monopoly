import board as b
from pathlib import Path

# Això troba la carpeta on està EL FITXER QUE ESTÀS ESCRIUENT ARA
BASE_DIR = Path(__file__).resolve().parent

# Ara unim la base amb la carpeta data
tiles_json_path = str(BASE_DIR / "data" / "tiles.json")
chance_json_path = str(BASE_DIR / "data" / "chance.json")
community_chest_json_path = str(BASE_DIR / "data" / "community-chest.json")
players_json_path = str(BASE_DIR / "data" / "players.json")

taulell = b.Board(tiles_json_path, chance_json_path, community_chest_json_path, players_json_path)

def test_board():
    assert isinstance(taulell.tiles(), list)

