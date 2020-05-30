from modules.hand_funcs import *
from modules.player_funcs import *

a = ['5♦', '3♦']
b = ['K♠', 'Q♠', '2♠', '8♠', '3♠']

class Card:
	def __init__(self, rank, suit):
		self.rank = rank
		self.suit = suit
	def __eq__(self, other):
		return self.rank == other.rank and self.suit == other.suit




# Player3 CARDS ['5♦', '3♦'] HAND Flush ['K♠', 'Q♠', '8♠', '3♦', '3♠', '2♠']
# Player4 CARDS ['A♦', '9♠'] HAND Flush ['K♠', 'Q♠', '9♠', '8♠', '3♠']
# Player1 CARDS ['8♣', '4♥'] HAND Flush ['K♠', 'Q♠', '8♣', '8♠', '3♠', '2♠']
# Player2 CARDS ['3♥', '2♣'] HAND Flush ['K♠', 'Q♠', '8♠', '3♥', '3♠', '2♣', '2♠']
# BOARD ['K♠', 'Q♠', '2♠', '8♠', '3♠']

hand = HandRank([Card(x[0],x[1]) for x in a] + [Card(x[0],x[1]) for x in b])

print(hand[0], PrintCards(hand[0]))
