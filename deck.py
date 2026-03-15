import json
import random
from card import Card, build_card

class Deck:
    """Represents a deck of cards loaded from a JSON configuration file."""

    _cards: list[Card]

    def __init__(self, path: str) -> None:
        """
        Initializes the deck by reading card data from a JSON file 
        and building Card objects using the factory function.
        """
        with open(path) as file:
            data = json.load(file)
        self._cards = [build_card(card_data) for card_data in data]

    def shuffle(self) -> None:
        """Shuffles the cards currently in the deck in a random order."""
        random.shuffle(self._cards)

    def draw(self) -> Card:
        """
        Removes and returns the top card from the deck.
        
        Raises:
            IndexError: If attempting to draw from an empty deck.
        """
        if not self._cards:
            raise IndexError("Cannot draw from an empty deck.")
        return self._cards.pop(0)

    def add_card(self, card: Card) -> None:
        """Places a card at the bottom of the deck."""
        self._cards.append(card)

    def size(self) -> int:
        """Returns the total number of cards currently in the deck."""
        return len(self._cards)