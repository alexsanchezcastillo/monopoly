from board import Board
from draw import draw
from slideshow import generate_slideshow
import os
from typing import Tuple

def play_game(board: Board, max_turns: int = 1000,
              output_prefix: str = "tauler", 
              output_dir: str = "games") -> Tuple[int, str]:
    """
    Play a complete game of Monopoly.
    
    Args:
        board: The game board
        max_turns: Maximum turns before stopping (default 1000)
        output_prefix: Prefix for SVG filenames
        output_dir: Directory to save SVG files to
    
    Returns:
        Tuple of (turn_count, winner_name)
    """
    
    os.makedirs(output_dir, exist_ok=True)

    # Save initial board state
    draw(board, os.path.join(output_dir, f"{output_prefix}-0000.svg"))
    
    turn_count = 0
    
    # Play game
    while len(board.players()) > 1:
        board.play_turn()
        turn_count += 1
        
        # Save board state after each turn
        svg_file_name = f"{output_prefix}-{turn_count:04d}.svg"
        draw(board, f"{output_dir}/{svg_file_name}")
        
        # Check for bankrupt players
        bankrupt_players = [p for p in board.players() if p.broke()]
        for player in bankrupt_players:
            creditor = player.creditor()
            if creditor is not None:
                # Bankrupt due to another player: all properties go to the creditor
                print(f"\n*** {player.name()} has gone BANKRUPT to {creditor.name()}! ***\n")
                for prop in list(player.owned_properties()):
                    prop.set_owner(creditor)
                    creditor.owned_properties().add(prop)
            else:
                # Bankrupt due to the bank: properties return to the bank
                print(f"\n*** {player.name()} has gone BANKRUPT to the bank! ***\n")
                for prop in list(player.owned_properties()):
                    prop.set_owner(None)
            player.owned_properties().clear()
            board.remove_player(player)
        
        # Check turn limit
        if turn_count >= max_turns:
            break

    
    # Game end — either one player left or turn limit reached
    if len(board.players()) == 1:
        winner = board.players()[0]
        print(f"\n*** {winner.name()} WINS THE GAME! ***")
        print(f"*** Final wealth: £{winner.money()} ***\n")
        return turn_count, winner.name()
    
    # Turn limit reached: richest player wins
    richest = max(board.players(), key=lambda p: p.money())
    print(f"\n*** Turn limit reached ({max_turns} turns)! ***")
    print(f"*** {richest.name()} WINS by wealth: £{richest.money()} ***\n")
    return turn_count, richest.name()


def main() -> None:
    """Main entry point for the game."""
    output_dir = "games"
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    else:
        # Remove all previous SVG files
        for file in os.listdir(output_dir):
            if file.endswith(".svg"):
                os.remove(os.path.join(output_dir, file))
    
    board = Board(
        tiles_json_path="data/tiles.json",
        chance_json_path="data/chance.json",
        community_chest_json_path="data/community-chest.json",
        players_json_path="data/players.json",
    )
    
    play_game(board, max_turns=500, 
              output_prefix="tauler", output_dir=output_dir)

    # Generate slideshow HTML with the new SVGs
    svg_files = sorted(f for f in os.listdir(output_dir) if f.endswith(".svg"))
    svg_paths = [os.path.join(output_dir, f) for f in svg_files]
    html = generate_slideshow(svg_paths)
    with open("game.html", "w") as f:
        f.write(html)
    print(f"Generated game.html with {len(svg_files)} frames.")


if __name__ == "__main__":
    main()