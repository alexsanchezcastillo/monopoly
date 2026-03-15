from board import Board
from tile import Street, Station, Utility, Tax
from player import Player

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

def test_street() -> None:
    """Tests buying a street and another player paying the correct rent."""
    board = create_test_board()
    owner = board.get_player(0)  
    visitor = board.get_player(1)
    
    # 1. Create a street (Price: 200, Rent: 50)
    street = Street(
        board=board, description="Test Street", position=1, name="Fake Street", 
        tile_type="property", color="blue", price=200, rent=50, 
        rent_with_color_set=100, rent_with_1_house=200, rent_with_2_houses=600, 
        rent_with_3_houses=1400, rent_with_4_houses=1700, rent_with_hotel=2000, 
        house_cost=50, hotel_cost=50, mortgage=100
    )
    
    # 2. Player 1 lands on it and buys it
    initial_money_owner = owner.money()
    street.land_on(owner)
    
    assert street.get_owner() == owner
    assert owner.money() == initial_money_owner - 200
    assert street in owner.owned_properties()
    
    # 3. Player 2 lands on it and pays rent
    initial_money_visitor = visitor.money()
    street.land_on(visitor)
    
    assert visitor.money() == initial_money_visitor - 50
    assert owner.money() == (initial_money_owner - 200) + 50

def test_station() -> None:
    """Tests that station rent scales with the number of stations owned."""
    board = create_test_board()
    owner = board.get_player(0)
    visitor = board.get_player(1)
    
    station1 = Station(
        board=board, description="S1", position=5, name="North Station", 
        tile_type="station", price=200, rent_with_1_station=25, 
        rent_with_2_stations=50, rent_with_3_stations=100, 
        rent_with_4_stations=200, mortgage=100
    )
    station2 = Station(
        board=board, description="S2", position=15, name="South Station", 
        tile_type="station", price=200, rent_with_1_station=25, 
        rent_with_2_stations=50, rent_with_3_stations=100, 
        rent_with_4_stations=200, mortgage=100
    )
    
    # Owner buys the first station and visitor lands on it (pays 25)
    station1.land_on(owner)
    
    visitor_money = visitor.money()
    station1.land_on(visitor)
    assert visitor.money() == visitor_money - 25
    
    # Owner buys the second station. Now rent for the first one goes up to 50
    station2.land_on(owner)
    
    visitor_money = visitor.money()
    station1.land_on(visitor)
    assert visitor.money() == visitor_money - 50

def test_utility() -> None:
    """Tests utility rent calculation by mocking the board's dice roll."""
    board = create_test_board()
    owner = board.get_player(0)
    visitor = board.get_player(1)
    
    utility = Utility(
        board=board, position=12, name="Water Works", tile_type="utility", 
        price=150, rent_multiplier=4, rent_multiplier_both=10, 
        description="Water Works", mortgage=75
    )
    utility.land_on(owner)
    
    visitor_money = visitor.money()
    
    board._current_dice = (3, 4)  # type: ignore
    utility.land_on(visitor)
        
    # Rent = sum of dice (7) * rent_multiplier (4) = 28
    assert visitor.money() == visitor_money - 28

def test_tax() -> None:
    """Tests that tax tiles charge the correct amount."""
    board = create_test_board()
    player = board.get_player(0)
    
    tax = Tax(
        board=board, position=4, name="Tax", tile_type="tax", 
        description="Pay 200 in taxes", amount=200
    )
    
    initial_money = player.money()
    tax.land_on(player)
    
    assert player.money() == initial_money - 200  

def test_property_owner_does_not_pay() -> None:
    """Tests that a player landing on their own property does not lose money."""
    board = create_test_board()
    owner = board.get_player(0)
    
    street = Street(
        board=board, description="My property", position=1, name="House", 
        tile_type="property", color="blue", price=200, rent=50, 
        rent_with_color_set=100, rent_with_1_house=200, rent_with_2_houses=600, 
        rent_with_3_houses=1400, rent_with_4_houses=1700, rent_with_hotel=2000, 
        house_cost=50, hotel_cost=50, mortgage=100
    )
    
    # Owner buys the property
    street.land_on(owner) 
    money_after_purchase = owner.money()
    
    # Owner lands on it again the next turn
    street.land_on(owner) 
    
    # Money shouldn't change
    assert owner.money() == money_after_purchase


def test_build_and_sell_houses_and_hotels():
    # --- SETUP ---
    board = create_test_board()
    player = Player(board=board, name="Richie", piece="Hat", color="blue", index=1)
    player.transaction(10000) # Give the player enough money to build
    
    street1 = Street(board, "Street 1", 1, "S1", "property", "blue", 200, 50, 100, 200, 600, 1400, 1700, 2000, 50, 50, 100)
    street2 = Street(board, "Street 2", 2, "S2", "property", "blue", 200, 50, 100, 200, 600, 1400, 1700, 2000, 50, 50, 100)

    player.buy_property(street1)
    player.buy_property(street2)

    # Mock board behavior to return the color group
    board.get_color_group = lambda color: [street1, street2] if color == "blue" else []

    # --- TEST 6.1: BUILD HOUSES & UNIFORM RULE ---
    assert street1.build_house(board) is True
    assert street1.num_houses() == 1  # Using the public getter
    
    # Uniform rule: cannot build a second house on street1 if street2 has 0
    assert street1.build_house(board) is False 
    
    # Build up to 4 houses legally step by step
    street2.build_house(board) # street2 now has 1
    
    for _ in range(3):
        street1.build_house(board)
        street2.build_house(board)

    # --- TEST 6.2: BUILD HOTEL ---
    assert street1.build_hotel(board) is True
    assert street1.has_hotel() is True
    assert street1.num_houses() == 0 
    
    # --- TEST 6.3: SELL BUILDINGS ---
    assert street1.sell_hotel() is True
    assert street1.has_hotel() is False
    assert street1.num_houses() == 4 
    
    assert street1.sell_house() is True
    assert street1.num_houses() == 3


def test_mortgages():
    # --- SETUP ---
    board = create_test_board()
    player = Player(board=board, name="Poor", piece="Dog", color="red", index=2)
    street = Street(board, "Test Street", 1, "TS", "property", "red", 200, 50, 100, 200, 600, 1400, 1700, 2000, 50, 50, 100)
    
    player.buy_property(street)
    
    initial_money = player.money()
    
    # --- TEST 7.1: MORTGAGE ---
    assert street.mortgage() is True
    assert street.is_mortgaged() is True
    assert player.money() == initial_money + 100 
    
    # --- TEST 7.2: FORGIVEN RENT ---
    visitor = Player(board=board, name="Visitor", piece="Car", color="green", index=3)
    visitor_money = visitor.money()
    street.land_on(visitor)
    
    # Visitor's money should remain unchanged
    assert visitor.money() == visitor_money 
    
    # --- TEST 7.3: UNMORTGAGE ---
    assert street.unmortgage() is True
    assert street.is_mortgaged() is False
    assert player.money() == initial_money - 10