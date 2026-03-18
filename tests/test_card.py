from board import Board
from card import build_card


# Factory tests - building all card types
def test_build_all_card_types() -> None:
    """Test building all card types from factory."""
    card_data: list[dict[str, str|int]] = [
        {"id": 1, "title": "Collect", "description": "Collect £100", 
         "action": "collect_money", "amount": 100},
        {"id": 2, "title": "Pay", "description": "Pay £50", 
         "action": "pay_money", "amount": 50},
        {"id": 3, "title": "Move to GO", "description": "Advance to GO", 
         "action": "move_to_position", "position": 0},
        {"id": 4, "title": "Go to Jail", "description": "Go directly to Jail", 
         "action": "go_to_jail", "position": 10},
        {"id": 5, "title": "Get Out of Jail", "description": "Get Out of Jail Free", 
         "action": "get_out_of_jail_card"},
        {"id": 6, "title": "Repairs", "description": "Pay for repairs",
         "action": "pay_per_property", "amountPerHouse": 25, "amountPerHotel": 100},
        {"id": 7, "title": "Station", "description": "Nearest Station",
         "action": "move_to_nearest_station", "rentMultiplier": 2},
    ]
    
    for data in card_data:
        card = build_card(data)
        assert card.title() == data["title"]
        assert card.id() == data["id"]


# Execution tests - verify cards execute correctly
def test_execute_all_card_types() -> None:
    """Test that all card types execute correctly."""
    board = Board("data/tiles.json", "data/chance.json",
                  "data/community-chest.json", "data/players.json")
    player = board.players()[0]
    
    # Test collect money
    initial_money = player.money()
    collect_data: dict[str, int|str] = {"id": 1, "title": "Collect", "description": "Collect £100",
                                        "action": "collect_money", "amount": 100}
    card = build_card(collect_data)
    card.execute(player, board)
    assert player.money() == initial_money + 100
    
    # Test pay money
    money_after_collect = player.money()
    pay_data: dict[str, int|str] = {"id": 2, "title": "Pay", "description": "Pay £50",
                                    "action": "pay_money", "amount": 50}
    card = build_card(pay_data)
    card.execute(player, board)
    assert player.money() == money_after_collect - 50
    
    # Test move
    move_data: dict[str, int|str] = {"id": 3, "title": "Move", "description": "Move to position",
                                     "action": "move_to_position", "position": 10}
    card = build_card(move_data)
    card.execute(player, board)
    assert player.position() == 10
    
    # Test jail
    jail_data: dict[str, int|str] = {"id": 4, "title": "Jail", "description": "Go to Jail",
                                     "action": "go_to_jail", "position": 10}
    card = build_card(jail_data)
    card.execute(player, board)
    assert player.is_in_jail()