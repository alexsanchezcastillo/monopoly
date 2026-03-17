from typing import TYPE_CHECKING
from tile import Street

if TYPE_CHECKING:
    from player import Player
    from tile import Property
    from board import Board

class Strategy:
    """
    A basic strategy that always buys a property if the player has enough money,
    and builds houses/hotels when possible.
    """

    def buy_property(self, player: Player, property_tile: Property) -> bool:
        """
        Returns True only if the player's current balance is greater than 
        or equal to the property's price.
        """
        return player.money() >= property_tile.price()

    def build(self, player: Player, board: Board) -> None:
        """
        Builds one house or hotel per turn on streets where the player has a monopoly.
        Only one build action per turn to make progression visible.
        """
        # Prioritize streets with fewer houses to build more evenly.
        streets = sorted(
            [p for p in player.owned_properties() if isinstance(p, Street)],
            key=lambda s: s.num_houses()
        )
        for street in streets:
            if street.can_build_hotel(board):
                street.build_hotel(board)
                return
            elif street.can_build_house(board):
                street.build_house(board)
                return