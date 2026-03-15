from typing import TYPE_CHECKING

# We use TYPE_CHECKING to avoid circular imports 
if TYPE_CHECKING:
    from player import Player
    from tile import Property, Street
    from board import Board


class PlayerStrategy:
    """
    Base class defining the decision-making of a player.
    Acts as an interface that other strategies will inherit from.
    """

    def buy_property(self, player: 'Player', property_tile: 'Property') -> bool:
        """
        Evaluates if the player should buy the given property.
        This method must be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement the buy_property method.")

    def build(self, player: 'Player', board: 'Board') -> None:
        """
        Decides whether to build houses/hotels on owned properties.
        Called at the end of each turn.
        """
        pass


class SimpleStrategy(PlayerStrategy):
    """
    A basic strategy that always buys a property if the player has enough money,
    and builds houses/hotels when possible.
    """

    def buy_property(self, player: 'Player', property_tile: 'Property') -> bool:
        """
        Returns True only if the player's current balance is greater than 
        or equal to the property's price.
        """
        return player.money() >= property_tile.price()

    def build(self, player: 'Player', board: 'Board') -> None:
        """
        Builds one house or hotel per turn on streets where the player has a monopoly.
        Only one build action per turn to make progression visible.
        """
        from tile import Street
        
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