from modules.hand_funcs import *
from modules.player_funcs import *

#and 2 pair

# a = ['A♦', 'A♥']
# a = ['Q♦', 'K♦']
a = ['A♠', 'A♦', 'A♥', '2♣', '3♥']

class Card:
	def __init__(self, rank, suit):
		self.rank = rank
		self.suit = suit
	def __eq__(self, other):
		return self.rank == other.rank and self.suit == other.suit


def reverse_enumerate(L):
	# Only works on things that have a len()
	l = len(L)
	for i, n in enumerate(L):
		yield l-i-1, n

# Player2 CARDS ['3♦', '2♥'] HAND Pair ['6♠', '6♦', '9♣', '8♥', '4♦'] 1.6908459408658885
# Player3 CARDS ['Q♥', '5♦'] HAND Pair ['6♠', '6♦', 'Q♥', '9♣', '8♥'] 1.690851911672734

cards = [Card(x[0],x[1]) for x in a]

hand = HandRank(cards)

weighted_rank_indexes = []

for idx, card in reverse_enumerate(hand['cards']):
	weighted_rank_indexes.append((RANKS().index(card.rank)+100)**(idx+1))

print(sum(weighted_rank_indexes))

#print(round(HANDS().index(hand) + sum(weighted_rank_indexes)/rank_divisor,2)

# st = round(HANDS().index(hand['hand']) + sum([RANKS().index(rank) for rank in [card.rank for card in hand['cards']]])/59.1,2)

print(hand['hand'], PrintCards(hand['cards']))