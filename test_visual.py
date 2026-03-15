from board import Board
from draw import draw

taulell = Board(
    "data/tiles.json", 
    "data/chance.json", 
    "data/community-chest.json", 
    "data/players.json"
)

# Manual movement test
# Get the first two players from the board
player_1 = taulell.get_player(0)
player_2 = taulell.get_player(1)

# Move player 1 by 5 steps (e.g., to 'Reading Railroad')
player_1.move(5)

# Move player 2 by 10 steps (e.g., to 'Just Visiting / In Jail' tile)
player_2.move(10)

# Move player 1 again to test wrap-around (pass GO)
# 5 + 37 = 42 -> wraps to tile 2 (Community Chest)
player_1.move(37) 

# Generate the SVG drawing with the updated positions

try:
    draw(taulell, "meu_tauler.svg")
    print("Success! Generated 'meu_tauler.svg'. Open it in a browser.")
except Exception as e:
    print(f"❌ Error en dibuixar: {e}")