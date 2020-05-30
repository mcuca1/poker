from modules.hand_funcs import *
from modules.player_funcs import *

a = ['K♥', 'K♠', '8♣', '8♠', 'A♣']
#b = ['5♠', 'Q♠', '2♠', '4♠', '3♠']

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

hand = HandRank([Card(x[0],x[1]) for x in a])

print(HANDS().index(hand['hand']))

st = round(2 + sum([RANKS().index(rank) for rank in [card.rank for card in hand['cards']]])/59.1,2)

print(hand['hand'], PrintCards(hand['cards']), st)
