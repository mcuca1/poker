from modules.hand_funcs import *
from modules.player_funcs import *

#and 2 pair

# a = ['A♦', 'A♥']
# a = ['Q♦', 'K♦']
# a = ['A♠', 'A♦', 'A♥', '2♣', '3♥']

class Card:
	def __init__(self, rank, suit):
		self.rank = rank
		self.suit = suit
	def __eq__(self, other):
		return self.rank == other.rank and self.suit == other.suit


# def reverse_enumerate(L):
# 	# Only works on things that have a len()
# 	l = len(L)
# 	for i, n in enumerate(L):
# 		yield l-i-1, n

# # Player2 CARDS ['3♦', '2♥'] HAND Pair ['6♠', '6♦', '9♣', '8♥', '4♦'] 1.6908459408658885
# # Player3 CARDS ['Q♥', '5♦'] HAND Pair ['6♠', '6♦', 'Q♥', '9♣', '8♥'] 1.690851911672734

# cards = [Card(x[0],x[1]) for x in a]

# hand = HandRank(cards)

# weighted_rank_indexes = []

# for idx, card in reverse_enumerate(hand['cards']):
# 	weighted_rank_indexes.append((RANKS().index(card.rank)+100)**(idx+1))

# print(sum(weighted_rank_indexes))

# #print(round(HANDS().index(hand) + sum(weighted_rank_indexes)/rank_divisor,2)

# # st = round(HANDS().index(hand['hand']) + sum([RANKS().index(rank) for rank in [card.rank for card in hand['cards']]])/59.1,2)

# print(hand['hand'], PrintCards(hand['cards']))


def PLAYERS(): 
	players = [	(['Player0', 500], {'debug_cards': ['6♣', '2♦']}), 
				(['Player1', 750], {'debug_cards': ['8♥', '5♣']}), 
				(['Player2', 800], {'debug_cards': ['8♣', '2♠']}), 
				(['Player3', 350], {'debug_cards': ['7♦', '2♣']})
				]
	#return players
	return [([p[0][0], ValueContainer(p[0][1])], p[1]) for p in players]

# deque([ Player(*args, **kwargs) for args in PLAYERS() ])

for args, kwargs in PLAYERS():
	print(args, kwargs)


printcards = ['6♣', '2♦']


cards = [ Card(card[0], card[1]) for card in printcards ]

print(cards)