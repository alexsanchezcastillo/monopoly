from deck import Deck
from card import Card

def test_deck_initialization_community() -> None:
    """Test that a Community Chest deck is properly initialized"""
    community_deck = Deck("data/community-chest.json")
    assert community_deck is not None
    chance_deck = Deck("data/chance.json")
    assert chance_deck is not None

def test_deck_draw_reduces_count() -> None:
    """Test that drawing returns a Card object 
    and reduces the deck size."""
    chance_deck = Deck("data/chance.json")
    initial_count = chance_deck.size()
    card = chance_deck.draw()
    assert isinstance(card, Card)  
    assert chance_deck.size() == initial_count - 1


def test_deck_shuffle_doesnt_crash() -> None:
    """Test that shuffling doesn't crash."""
    chance_deck = Deck("data/chance.json")
    chance_deck.shuffle()
    assert chance_deck.size() > 0


def test_deck_size_method() -> None:
    """Test the size method."""
    chance_deck = Deck("data/chance.json")
    initial_size = chance_deck.size()
    chance_deck.draw()
    assert chance_deck.size() == initial_size - 1


def test_deck_add_card() -> None:
    """Test adding a card to the deck."""
    community_deck = Deck("data/community-chest.json")
    initial_size = community_deck.size()
    
    # Draw a card
    card = community_deck.draw()
    assert community_deck.size() == initial_size - 1
    
    # Add it back
    community_deck.add_card(card)
    assert community_deck.size() == initial_size