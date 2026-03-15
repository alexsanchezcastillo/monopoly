import pickle
import json
from player import Player, build_player
from tile import Tile, build_tile
from tile import Property, Street
import random
from deck import Deck


class Board:
    """Represents the complete Monopoly game board, including tiles, card decks, and players.
    
    Manages all game logic: dice rolling, turn progression, jail handling,
    building phases, and win/loss conditions.
    """
    _tiles_path: str
    _chance_path: str
    _community_chest_path: str
    _players_path: str
    _list_tiles: list[Tile]
    _list_chance: Deck
    _list_community_chest: Deck
    _list_players: list[Player]
    _current_dice: tuple[int, int]   # important information in every stage of the game, it is actualized in every dice 
    _current_player_index: int       # important information in every stage of the game, it is actualized in every turn
    
    def __init__(
        self,
        tiles_json_path: str,
        chance_json_path: str,
        community_chest_json_path: str,
        players_json_path: str,
    ):
        self._tiles_path = tiles_json_path
        self._chance_path = chance_json_path
        self._community_chest_path = community_chest_json_path
        self._players_path = players_json_path

        self._current_dice = (1, 1)
        self._current_player_index = 0

        with open(tiles_json_path, 'r', encoding='utf-8') as f:
            tiles_data = json.load(f)
            self._list_tiles = [build_tile(self, data) for data in tiles_data]

        with open(chance_json_path, 'r', encoding='utf-8') as f:
            self._list_chance = json.load(f)

        with open(community_chest_json_path, 'r', encoding='utf-8') as f:
            self._list_community_chest = json.load(f)

        with open(players_json_path, 'r', encoding='utf-8') as f:
            players_data = json.load(f)
            # Assign an index to each player based on their order in the JSON file.
            self._list_players = [
                build_player(self, data, i) for i, data in enumerate(players_data)
            ]
        
        self._chance_deck = Deck(chance_json_path)
        self._community_chest_deck = Deck(community_chest_json_path)

    def roll_dice(self) -> tuple[int, int]:
        """
        Rolls two six-sided dice, updates the internal state, 
        and returns the result.
        """
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        self._current_dice = (dice1, dice2)
        return self._current_dice

    def current_player(self) -> Player:
        """Returns the player whose turn it is."""
        return self._list_players[self._current_player_index]

    def next_player(self) -> None:
        """Passes the turn to the next player in the list."""
        self._current_player_index = (self._current_player_index + 1) % len(self._list_players)

    def play_turn(self) -> None:
        """
        Executes a full turn: handles jail, rolls dice, detects doubles,
        moves the piece, executes tile actions, and manages turn progression.
        """
        player = self.current_player()
        
        # Handle jail entry/exit first
        if player.is_in_jail():
            print(f"[JAIL] {player.name()} is in jail (turn {player.turns_in_prison()}/3).")
            
            # Try to exit jail using a card
            if player.get_out_of_jail_cards() > 0:
                if player.use_get_out_of_jail_card():
                    print(f"[JAIL] {player.name()} used a Get Out of Jail Free card!")
            
            # If still in jail, try to roll doubles or serve time
            if player.is_in_jail():
                player.increment_jail_turn()
                d1, d2 = self.roll_dice()
                is_double = (d1 == d2)
                
                print(f"[JAIL] {player.name()} rolls {d1} and {d2}.")
                
                if is_double:
                    # Exit jail with doubles
                    player.exit_jail()
                    print(f"[JAIL] {player.name()} rolled doubles! Exiting jail.")
                    # Continue with normal movement
                    steps = d1 + d2
                    player.move(steps)
                    print(f"       {player.name()} lands on tile {player.position()}.")
                    tile = self.get_tile(player.position())
                    tile.land_on(player)
                elif player.turns_in_prison() >= 3:
                    # Auto-exit after 3 turns
                    player.exit_jail()
                    print(f"[JAIL] {player.name()} completed 3 jail turns. Released.")
                    # Do NOT roll or move - just pass turn
                else:
                    print(f"[JAIL] {player.name()} stays in jail.")
                
                self.next_player()
                return
        
        # Normal turn logic (not in jail)
        doubles_count = 0
        
        while True:
            d1, d2 = self.roll_dice()
            steps = d1 + d2
            is_double = (d1 == d2)
            
            print(f"[TURN] {player.name()} rolls {d1} and {d2} (Total: {steps}).")
            
            if is_double:
                doubles_count += 1
                print(f"       Double roll! ({doubles_count}/3)")
                
                if doubles_count == 3:
                    print(f"       3 consecutive doubles! {player.name()} goes directly to jail.")
                    player.go_to_jail(self.jail_position())
                    break  # Turn ends immediately
            
            # Normal movement
            player.move(steps)
            print(f"       {player.name()} lands on tile {player.position()}.")
            
            # Execute tile action
            tile = self.get_tile(player.position())
            tile.land_on(player)
            
            # If it's not a double or player went broke, end turn
            if not is_double or player.broke():
                break
        
        # Building phase: let the player build houses/hotels
        if not player.broke():
            player.strategy().build(player, self)

        # Always pass the turn to the next player at the end
        self.next_player()

    def players(self) -> list[Player]:
        """Returns a list with all the players."""
        return self._list_players
    
    def get_player(self, index: int) -> Player:
        """Returns the player at the specified index."""
        return self._list_players[index]

    def tiles(self) -> list[Tile]:
        return self._list_tiles
    
    def size(self) -> int:
        """Returns the total number of tiles on the board."""
        return len(self._list_tiles)
    
    def dice(self) -> tuple[int, int]:
        """Returns the most recent dice roll result."""
        return self._current_dice

    def num_tiles(self) -> int:
        return len(self._list_tiles)

    def jail_position(self) -> int:
        return 10

    def current_dice(self) -> tuple[int, int]:
       return self._current_dice
    
    def get_tile(self, index: int) -> Tile:
        return self._list_tiles[index % self.num_tiles()]
    
    def get_property(self, index: int) -> Property:
        tile = self.tiles()[index]
        if isinstance(tile, Property):
            return tile
        else:
            raise AttributeError(f"Tile '{tile.name()}' is not of type property.")
        
    def move_to_nearest_station(self, player: Player, multiplier: int = 1) -> None:
        """
        Moves the player to the nearest station ahead of them.
        Stations are typically at positions 5, 15, 25, and 35.
        """
        # Define station positions
        stations = [5, 15, 25, 35]
        self.move_to_nearest(player, stations, multiplier)

    def move_to_nearest_utility(self, player: Player, multiplier: int = 1) -> None:
        """
        Moves the player to the nearest utility (Electric Company or Water Works).
        """
        # Define utility positions
        utilities = [12, 28]
        self.move_to_nearest(player, utilities, multiplier)

    def move_to_nearest(self, player: Player, targets: list[int], multiplier: int) -> None:
        """
        Helper method to find the next target position and move the player.
        If no target is ahead, it wraps around to the first target of the next lap.
        """
        current_pos = player.position()
        
        # Find the first target position that is greater than current position
        # If the list is empty (all targets are behind), take the first one (lap wrap)
        next_target = next((pos for pos in targets if pos > current_pos), targets[0])
        
        # Execute the move
        player.move_to(next_target)
        
        # Note: The multiplier logic (e.g., pay 10x dice roll) should be handled 
        # by the Square's landing logic or a flag in the Player's state.
        
    def get_color_group(self, color: str) -> list[Property]:
        """Returns a list of all streets of a specific color group."""
        return [tile for tile in self._list_tiles 
                if isinstance(tile, Street) and tile.color() == color]

    def play(self) -> None:
        """Executes the game loop until only one player remains solvent."""
        while len(self._list_players) > 1:
            self.play_turn()
            
            # Check if any player went broke after the turn
            bankrupt_players = [p for p in self._list_players if p.broke()]
            for player in bankrupt_players:
                print(f"\n*** {player.name()} has gone BANKRUPT! ***\n")
                self._list_players.remove(player)
        
        # Game ends when only one player remains
        if len(self._list_players) == 1:
            winner = self._list_players[0]
            print(f"\n*** {winner.name()} WINS THE GAME! ***")
            print(f"*** Final wealth: M{winner.money()} ***\n")
    
    def chance_deck(self) -> Deck:
        return self._chance_deck
    
    def community_chest_deck(self) -> Deck:
        return self._community_chest_deck
    
    def has_monopoly(self, player: Player, color: str) -> bool:
        """Returns True if the player owns all properties of the given color."""
        color_group = self.get_color_group(color)
        if not color_group:
            return False
        return all(p.get_owner() == player for p in color_group)

def save_board(board: Board, pickle_path: str) -> None:
    """Saves the board in the document named pickle_path."""
    with open(pickle_path, "wb") as f:  # wb = write binary
        pickle.dump(board, f)

def load_board(pickle_path: str) -> Board:
    """Retrieves the data saved in the document named pickle_path."""
    with open(pickle_path, "rb") as f:  # rb = read binary
        return pickle.load(f)