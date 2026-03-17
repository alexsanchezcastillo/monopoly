import pytest
from strategy import Strategy
from player import Player
from tile import Street
from board import Board
# from your_path import create_test_board  # Uncomment if you need a real board

def create_test_board() -> Board:
    """
    Helper function to create a fresh Board instance for testing.
    It uses simple relative paths to the JSON files.
    """
    return Board(
        "data/tiles.json",
        "data/chance.json",
        "data/community-chest.json",
        "data/players.json"
    )


def test_strategy_buys_with_enough_money() -> None:
    """Tests that Strategy decides to buy when the player has enough money."""
    strategy = Strategy()
    board = create_test_board()  
    
    street = Street(
        board=board, description="Test Street", position=1, name="Fake Street", 
        tile_type="property", color="blue", price=200, rent=50, 
        rent_with_color_set=100, rent_with_1_house=200, rent_with_2_houses=600, 
        rent_with_3_houses=1400, rent_with_4_houses=1700, rent_with_hotel=2000, 
        house_cost=50, hotel_cost=50, mortgage=100
    )
    
    # Case 1: Player has more than enough money
    rich_player = Player(board=board, name="Rich", piece="Car", color="blue", index=1)
    assert strategy.buy_property(rich_player, street) is True
    
    # Case 2: Player has exactly the required money
    exact_player = Player(board=board, name="Exact", piece="Hat", color="green", index=2)
    assert strategy.buy_property(exact_player, street) is True


def test_strategy_declines_without_money() -> None:
    """Tests that Strategy decides NOT to buy when funds are insufficient."""
    strategy = Strategy()
    board = create_test_board()  
    
    street = Street(
        board=board, description="Test Street", position=1, name="Fake Street", 
        tile_type="property", color="blue", price=200, rent=50, 
        rent_with_color_set=100, rent_with_1_house=200, rent_with_2_houses=600, 
        rent_with_3_houses=1400, rent_with_4_houses=1700, rent_with_hotel=2000, 
        house_cost=50, hotel_cost=50, mortgage=100
    )
    
    # Player cannot afford the 200 price
    poor_player = Player(board=board, name="Poor", piece="Dog", color="yellow", index=3)
    poor_player.transaction(-1400)  # Reduce money to 100, which is less than the price
    
    assert strategy.buy_property(poor_player, street) is False