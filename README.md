# Monopoly Game Implementation

A comprehensive Python implementation of the classic Monopoly board game with automated player strategies and SVG visualization support.

## Project Overview

This project implements the complete logic of the Monopoly board game, allowing multiple players (2-4) to compete against each other. The game features:

- **Complete game mechanics**: Properties, houses, hotels, mortgages, and utility rent calculations
- **Automated players**: AI-driven players make decisions based on strategies
- **Dice mechanics**: Proper handling of doubles and jail system
- **Card system**: Chance and Community Chest cards with diverse effects
- **Visualization**: SVG-based board rendering and slideshow generation
- **Extensible design**: Strategy pattern for easy addition of new AI strategies

## Architecture

### Core Modules

- **`const.py`**: Game constants (GO salary, starting money, etc.)
- **`tile.py`**: Tile hierarchy (base class with specialized types: Property, Street, Station, Utility, Tax, etc.)
- **`player.py`**: Player representation and state management
- **`strategy.py`**: Strategy pattern for AI decision-making
- **`card.py`**: Card system for Chance and Community Chest
- **`deck.py`**: Card deck with shuffle and draw operations
- **`board.py`**: Main game board managing all game state and rules
- **`draw.py`**: SVG visualization of board state
- **`slideshow.py`**: HTML slideshow generator for game visualization
- **`main.py`**: Game entry point

## Key Features Implemented

### Game Rules
- **Players**: 2-4 players starting with M1500 at GO position
- **Movement**: Dice rolls with passes GO collecting M200 salary
- **Doubles**: Extra turn mechanic, 3 doubles sends to jail
- **Properties**: Streets, stations, utilities with proper rent calculations
- **Monopolies**: Double rent when owning complete color set
- **Jail System**: Entry from doubles/cards, exit via doubles/card/3 turns
- **Houses & Hotels**: Build on streets with uniform building rules
- **Mortgages**: Can mortgage properties for 50% value, unmortgage for +10% interest
- **Cards**: Chance and Community Chest with 16 cards each
- **Bankruptcy**: Players eliminated when unable to pay debts

### Player Strategies
The `SimpleStrategy` implementation:
- Buys properties if cash ≥ property price
- Does not build houses/hotels
- Can be extended for more sophisticated strategies

## Code Quality

- ✅ 24/24 tests passing
- ✅ 0 type errors (mypy validation)
- ✅ Full type annotations
- ✅ Clean architecture with inheritance and polymorphism
- ✅ Factory pattern for object creation
- ✅ Comprehensive documentation

## Usage

### Running a Game
```bash
python main.py
```

Plays a complete game and saves board states as `tauler-NNNN.svg` files.

### Running Tests
```bash
pytest              # Run all tests
pytest -v          # Verbose output
pytest test_tile.py -v  # Specific test file
```

### Type Checking
```bash
mypy *.py          # Check all type annotations
```

### Generating Visualization
```bash
python slideshow.py game.html tauler-*.svg
```

Creates an interactive HTML slideshow showing game progression.

## Installation

### Requirements
- Python 3.8+
- `drawsvg` library for SVG graphics

### Setup
```bash
pip install drawsvg
```

## Test Coverage

Comprehensive test suite including:
- Board initialization and data loading
- Player movement and GO collection
- Property purchase and rent mechanics
- House/hotel building with monopoly checking
- Mortgage operations with interest calculation
- Doubles detection and jail mechanics
- Card drawing and execution
- Strategy decision-making

## Design Patterns

- **Inheritance**: Tile and Card hierarchies use polymorphism
- **Factory Pattern**: `build_tile()` and `build_card()` functions create objects from JSON
- **Strategy Pattern**: `PlayerStrategy` interface with plug-in implementations
- **Composition**: Board composes tiles, players, and card decks

## Implementation Highlights

### Property Management
- Land on unowned property triggers purchase decision via strategy
- Rent calculation respects mortgages, monopolies, and buildings
- Uniform building rules enforced for houses and hotels
- Complete bankruptcy handling with asset liquidation

### Jail System
- Entry: Via doubles or landing on "Go To Jail"
- Exit: Via doubles roll, "Get Out of Jail Free" card, or 3 turns
- No payment required (simplified from official rules)
- Proper state tracking for multi-turn imprisonment

### Card System
- 16 different card types with specialized behaviors
- Cards returned to deck after use (except "Get Out of Jail Free")
- Full polymorphic implementation of card effects

## File Structure

```
programa/
├── board.py              # Main game engine
├── card.py              # Card definitions
├── const.py             # Game constants
├── deck.py              # Card deck
├── draw.py              # SVG rendering
├── drawsvg.pyi          # Type stubs
├── main.py              # Entry point
├── player.py            # Player class
├── slideshow.py         # HTML generator
├── strategy.py          # AI strategies
├── tile.py              # Tile hierarchy
├── test_*.py            # Test suite
├── README.md            # This file
└── data/                # JSON configuration
    ├── tiles.json
    ├── chance.json
    ├── community-chest.json
    └── players.json
```

## Game Configuration

Board and card configuration loaded from JSON:
- `data/tiles.json`: Complete board layout with 40 tiles
- `data/chance.json`: 16 Chance cards
- `data/community-chest.json`: 16 Community Chest cards
- `data/players.json`: Player definitions (4 players: Jordi, Mireia, Arnau, Marta)

## Future Enhancements

- Advanced AI strategies with property evaluation
- Trading between players
- Auction system for unpurchased properties
- Interactive mode with human players
- Network multiplayer support
- Replay system with game recording

## Notes

- Game termination: Last solvent player wins
- Turn order preserved: Players play in JSON order
- Random seed: `seed(25)` for reproducible games
- Safety: 1000-turn limit prevents infinite loops
