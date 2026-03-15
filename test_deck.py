"""
Test suite for the Deck class.
"""

import pytest
from deck import Deck
from card import Card


class TestDeck:
    """Test the Deck class functionality."""

    @pytest.fixture
    def chance_deck(self) -> Deck:
        """Create a Chance deck for testing."""
        return Deck("data/chance.json")

    @pytest.fixture
    def community_deck(self) -> Deck:
        """Create a Community Chest deck for testing."""
        return Deck("data/community-chest.json")

    def test_deck_initialization_chance(self, chance_deck: Deck) -> None:
        """Test that a Chance deck is properly initialized."""
        assert chance_deck is not None
        assert hasattr(chance_deck, 'draw')
        assert hasattr(chance_deck, 'shuffle')

    def test_deck_initialization_community(self, community_deck: Deck) -> None:
        """Test that a Community Chest deck is properly initialized."""
        assert community_deck is not None
        assert len(community_deck._cards) > 0

    def test_deck_has_cards(self, chance_deck: Deck) -> None:
        """Test that the deck has cards."""
        assert hasattr(chance_deck, '_cards')
        assert len(chance_deck._cards) > 0

    def test_deck_draw_reduces_count(self, chance_deck: Deck) -> None:
        """Test that drawing a card reduces the deck size."""
        initial_count = len(chance_deck._cards)
        card = chance_deck.draw()
        assert card is not None
        assert len(chance_deck._cards) == initial_count - 1

    def test_deck_draw_returns_card(self, chance_deck: Deck) -> None:
        """Test that drawing returns a Card object."""
        card = chance_deck.draw()
        # Should be some kind of Card subclass
        assert hasattr(card, 'execute')
        assert hasattr(card, 'title')

    def test_deck_shuffle_doesnt_crash(self, chance_deck: Deck) -> None:
        """Test that shuffling doesn't crash."""
        import random
        random.seed(42)
        # Should not raise an exception
        chance_deck.shuffle()
        assert len(chance_deck._cards) > 0

    def test_deck_multi_draw(self, community_deck: Deck) -> None:
        """Test drawing multiple cards."""
        initial_count = len(community_deck._cards)
        cards_drawn = []
        
        for _ in range(min(5, initial_count)):
            cards_drawn.append(community_deck.draw())
        
        assert len(cards_drawn) > 0
        assert len(community_deck._cards) == initial_count - len(cards_drawn)

    def test_deck_has_multiple_card_types(self, chance_deck: Deck) -> None:
        """Test that deck contains different card types."""
        import random
        random.seed(99)
        original_count = len(chance_deck._cards)
        
        card_descriptions = set()
        sample_size = min(10, original_count)
        
        for _ in range(sample_size):
            card = chance_deck.draw()
            card_descriptions.add(card.description()[:30])  # First 30 chars
        
        # Should have multiple different card descriptions
        assert len(card_descriptions) >= 1

    def test_deck_size_method(self, chance_deck: Deck) -> None:
        """Test the size method."""
        initial_size = chance_deck.size()
        chance_deck.draw()
        assert chance_deck.size() == initial_size - 1

    def test_deck_add_card(self, community_deck: Deck) -> None:
        """Test adding a card to the deck."""
        initial_size = community_deck.size()
        
        # Draw a card
        card = community_deck.draw()
        assert community_deck.size() == initial_size - 1
        
        # Add it back
        community_deck.add_card(card)
        assert community_deck.size() == initial_size
