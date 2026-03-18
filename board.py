import pickle
import json
from player import Player, build_player
from tile import Tile, build_tile
from tile import Property, Street
import random
from deck import Deck


class Board:
    """Represents the complete Monopoly game board, including tiles, card decks, and players.
    Manages all game logic: dice rolling, turns, jail mechanics...
    """
    _tiles_path: str
    _chance_path: str
    _community_chest_path: str
    _players_path: str
    _list_tiles: list[Tile]
    _list_chance: Deck
    _list_community_chest: Deck
    _list_players: list[Player]
    _current_dice: tuple[int, int]
    _current_player_index: int
    
    def __init__(
        self,
        tiles_json_path: str,
        chance_json_path: str,
        community_chest_json_path: str,
        players_json_path: str,
    ):
        """Initializes the board by loading tiles, cards and players from the given JSON files."""
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
        
        # Handle jail first
        if player.is_in_jail():
            print(f"{player.name()} is in jail (turn {player.turns_in_prison()}/3).")
            
            # Try to exit jail using a card
            if player.get_out_of_jail_free_cards() > 0:
                if player.use_get_out_of_jail_card():
                    print(f"{player.name()} used a Get Out of Jail Free card!")
            
            # If still in jail, try to roll doubles or serve time
            if player.is_in_jail():
                player.increment_jail_turn()
                d1, d2 = self.roll_dice()
                is_double = (d1 == d2)
                
                print(f"{player.name()} rolls {d1} and {d2}.")
                
                if is_double:
                    # Exit jail with doubles
                    player.exit_jail()
                    print(f"{player.name()} rolled doubles! Exiting jail.")
                    # Continue with normal movement
                    steps = d1 + d2
                    player.move(steps)
                    print(f"{player.name()} lands on tile {player.position()}.")
                    tile = self.get_tile(player.position())
                    tile.land_on(player)
                elif player.turns_in_prison() >= 3:
                    # Auto-exit after 3 turns
                    player.exit_jail()
                    print(f"{player.name()} completed 3 jail turns. Released.")
                    # Do NOT roll or move - just pass turn
                else:
                    print(f"{player.name()} stays in jail.")
                
                self.next_player()
                return
        
        # Normal turn logic (not in jail)
        doubles_count = 0
        
        while True:
            d1, d2 = self.roll_dice()
            steps = d1 + d2
            is_double = (d1 == d2)
            
            print(f"{player.name()} rolls {d1} and {d2} (Total: {steps}).")
            
            if is_double:
                doubles_count += 1
                print(f"Double roll! ({doubles_count}/3)")
                
                if doubles_count == 3:
                    print(f"3 consecutive doubles! {player.name()} goes to jail.")
                    player.go_to_jail(self.jail_position())
                    break  # Turn ends immediately
            
            # Normal movement
            player.move(steps)
            print(f"{player.name()} lands on tile {player.position()}.")
            
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

    def remove_player(self, player: Player) -> None:
        """Removes the given player from the game and adjusts the turn index."""
        player_idx = self._list_players.index(player)
        self._list_players.remove(player)
        if player_idx < self._current_player_index:
            self._current_player_index -= 1
        if self._current_player_index >= len(self._list_players) and len(self._list_players) > 0:
            self._current_player_index = 0

    def players(self) -> list[Player]:
        """Returns a list with all the players."""
        return self._list_players
    
    def get_player(self, index: int) -> Player:
        """Returns the player at the given index."""
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
        """Returns the total number of tiles on the board."""
        return len(self._list_tiles)

    def jail_position(self) -> int:
        """Returns the index of the Jail tile."""
        return 10

    def current_dice(self) -> tuple[int, int]:
       """Returns the most recent dice roll result."""
       return self._current_dice
    
    def get_tile(self, index: int) -> Tile:
        """Returns the tile at the given index (wraps around if out of bounds)."""
        return self._list_tiles[index % self.num_tiles()]
    
    def get_property(self, index: int) -> Property:
        """Returns the property tile at the given index, or raises AttributeError if it's not a property."""
        tile = self.tiles()[index]
        if isinstance(tile, Property):
            return tile
        else:
            raise AttributeError(f"Tile '{tile.name()}' is not of type property.")
        
    def move_to_nearest_station(self, player: Player, multiplier: int = 1) -> None:
        """Moves the given player to the nearest station ahead, applying the rent multiplier."""
        # Station positions
        stations = [5, 15, 25, 35]
        self.move_to_nearest(player, stations, multiplier)

    def move_to_nearest_utility(self, player: Player, multiplier: int = 1) -> None:
        """Moves the given player to the nearest utility, applying the rent multiplier."""
        # Utility positions
        utilities = [12, 28]
        self.move_to_nearest(player, utilities, multiplier)

    def move_to_nearest(self, player: Player, targets: list[int], multiplier: int) -> None:
        """Finds the next target position, moves the player, and handles
        the rent with the given multiplier (from Chance card rules).
        If unowned, the player may buy it. If owned, rent is multiplied."""
        current_pos = player.position()
        
        next_target = None
        for pos in targets:
            if pos > current_pos:
                next_target = pos
                break
        if next_target is None:
            next_target = targets[0]
        
        player.move_to(next_target)
        
        tile = self.get_tile(next_target)
        if not isinstance(tile, Property):
            return
        
        if tile.is_mortgaged():
            return
        
        owner = tile.get_owner()
        if owner is None:
            # Unowned: offer purchase as normal
            if player.decide_buy(tile):
                player.transaction(-tile.price())
                tile.set_owner(player)
                player.owned_properties().add(tile)
        elif owner != player:
            # Owned by another player: pay rent × multiplier
            rent = tile.get_rent() * multiplier
            player.set_creditor(owner)
            player.transaction(-rent)
            owner.transaction(rent)
        
    def get_color_group(self, color: str) -> list[Property]:
        """Returns a list of all streets of the given color."""
        return [tile for tile in self._list_tiles 
                if isinstance(tile, Street) and tile.color() == color]
    
    def chance_deck(self) -> Deck:
        """Returns the Chance card deck."""
        return self._chance_deck
    
    def community_chest_deck(self) -> Deck:
        """Returns the Community Chest card deck."""
        return self._community_chest_deck
    
    def has_monopoly(self, player: Player, color: str) -> bool:
        """Returns True if the given player owns all properties of the given color."""
        color_group = self.get_color_group(color)
        if not color_group:
            return False
        return all(p.get_owner() == player for p in color_group)

def save_board(board: Board, pickle_path: str) -> None:
    """Saves the board state to a pickle file at the given path."""
    with open(pickle_path, "wb") as f:  # wb = write binary
        pickle.dump(board, f)

def load_board(pickle_path: str) -> Board:
    """Loads and returns a board from a pickle file at the given path."""
    with open(pickle_path, "rb") as f:  # rb = read binary
        return pickle.load(f)