from board import Board
from const import START_MONEY, GO_SALARY


def create_test_board() -> Board:
    """
    Helper function to create a fresh Board instance.
    We need the board because players are initialized with it.
    """
    return Board(
        "data/tiles.json",
        "data/chance.json",
        "data/community-chest.json",
        "data/players.json",
    )


def test_player_initial_state() -> None:
    """Tests that a new player has the correct default state."""
    board = create_test_board()
    player = board.current_player()

    assert player.position() == 0
    assert player.money() == START_MONEY
    assert isinstance(player.name(), str)
    assert isinstance(player.color(), str)
    assert isinstance(player.piece(), str)
    assert player == board.get_player(0)
    assert player.board() == board
    assert isinstance(player.index(), int)
    assert player.get_out_of_jail_free_cards() == 0
    assert player.turns_in_prison() == 0
    assert player.owned_properties() == set()


def test_player_basic_move() -> None:
    """Tests if the player moves the correct number of steps."""
    board = create_test_board()
    player = board.get_player(0)
    initial_money = player.money()
    player.move(5)

    assert player.position() == 5
    assert player.money() == initial_money  # money should not change


def test_player_pass_go_salary() -> None:
    """Tests if the player collects GO_SALARY when passing GO."""
    board = create_test_board()
    player = board.get_player(0)
    # We move the player close to GO and then move enough steps to pass it
    player.move(38)
    money_before_go = player.money()
    player.move(5)

    assert player.position() == 3
    assert player.money() == money_before_go + GO_SALARY


def test_player_financials() -> None:
    """Tests the transaction method and the broke status."""
    board = create_test_board()
    player = board.current_player()
    initial_money = player.money()

    # Test transaction: earning money
    player.transaction(200)
    assert player.money() == initial_money + 200
    assert player.broke() is False  # Player has money, so not broke

    # Test transaction: losing money and going broke
    player.transaction(-(player.money() + 100))  # We take all money + 100 extra
    assert player.money() < 0
    assert player.broke() is True
