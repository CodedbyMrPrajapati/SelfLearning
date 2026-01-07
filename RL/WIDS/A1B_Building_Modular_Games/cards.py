from enum import Enum
import pygame
import random
class Suits(Enum):
    SPADES = 1
    HEARTS = 2
    CLUBS  = 3
    DIAMONDS = 4

class Card:
    def __init__(self, suit: Suits, rank: int):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        match self.rank:
            case 1:
                rank_str = 'A'
            case 11:
                rank_str = 'J'
            case 12:
                rank_str = 'Q'
            case 13:
                rank_str = 'K'
            case _:
                rank_str = str(self.rank)

        match self.suit:
            case Suits.SPADES:
                suit_str = u'\u2660'
            case Suits.HEARTS:
                suit_str = u'\u2665'
            case Suits.CLUBS:
                suit_str = u'\u2663'
            case Suits.DIAMONDS:
                suit_str = u'\u2666'

        return f"{rank_str}{suit_str}"

    def __repr__(self):
        return f"Card({self.suit.name}, {self.rank})"
        
class Deck:
    def __init__(self):
        self.cards = [Card(suit,rank) for suit in Suits for rank in range(1,14)]
    def reset(self):
        self.cards = [Card(suit,rank) for suit in Suits for rank in range(1,14)]
    def shuffle(self):
        random.shuffle(self.cards)
    def draw(self):
        if not self.cards : return None
        return self.cards.pop()
    
class Hand:
    def __init__(self):
        self.cards = []
    
    def add_card(self,card:Card):
        self.cards.append(card)
    def flush(self,card:Card):
        self.cards = []
    def value(self):
        total = 0
        aces = 0
        for card in self.cards:
            if card.value == 1:
                aces += 1 
            else:
                total += min(card.value,10)
        for _ in range(aces):
            if total + 11 <= 21:
                total += 11
            else:
                total += 1
        return total
    def __str__(self):
        if not self.cards:
            return "(empty hand)"
        lines = ["___ " * 4, "", "", ""]
        for card in self.cards:
            repr = str(card)
            lines[1] += f"|{repr[-1]:<2}| "
            lines[2] += f"| {repr[:-1]} | "
            lines[3] += f"|{repr[-1]:>2}| " 
        return "\n".join(lines)
deck = Deck()
deck.shuffle()

player = Hand()
player.add_card(deck.draw())
player.add_card(deck.draw())

print("Your hand:", player)
print("Value:", player.value())
print(player.ascii())
