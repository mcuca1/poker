import random
from random import shuffle
import numpy as np
from collections import deque
import inspect

def HandRank(cards):
	# A hand are the 5 best cards!
	cards_per_hand = 5
	def SortCardsByRank(cards):
		rankdict = dict([(t[1], t[0]) for t in list(enumerate(RANKS()))])
		cards.sort(key=lambda x: rankdict[x.rank], reverse=True)
		return cards
	# Pairs, sets and quads are one rank hands, changing only the number of cards
	def OneRankHand(cards, n):
		# Kickers are the best cards left between the hand and the total 5
		kickers = cards_per_hand - n
		# Return highest pair + highest 3 cards left
		highest_rankhand = False
		for rank in [x.rank for x in SortCardsByRank(cards)]:
			if sum(card.rank == rank for card in cards) == n: highest_rankhand = [card for card in cards if card.rank == rank]
			if highest_rankhand: break
		if highest_rankhand:
			for card in highest_rankhand: cards.remove(card)
			cards = SortCardsByRank(cards)[:kickers]
			return highest_rankhand + cards
		return []
	def HighCard(cards):
		# Return 5 highest cards
		return SortCardsByRank(cards)[:cards_per_hand]
	def Pair(cards):
		return OneRankHand(cards, 2)
	# def TwoPair(cards):
	# 	# Kickers are the best cards left between the hand and the total 5
	# 	kickers = 1
	# 	pairs = []
	# 	for rank in [x.rank for x in SortCardsByRank(cards)]:
	# 		if sum(card.rank == rank for card in cards) == 2: pairs.append([card for card in cards if card.rank == rank])
	# 	if len(pairs) >=2:
	# 		for card in [card for pair in pairs[:2] for card in pair]: cards.remove(card)
	# 		kicker = SortCardsByRank(cards)[0]
	# 		return [card for pair in pairs[:2] for card in pair] + kicker
	# 	return []
	# def Set(cards):
	# 	return OneRankHand(cards, 3)
	# def Quads(cards):
	# 	return OneRankHand(cards, 4)
	# Exec all hand functions, the first strongest we find is our hand
	for hand in reversed(HANDS()):
		try:
			hand_cards = locals()[hand](cards)
			if any(hand_cards): return (hand, hand_cards)
		except KeyError:
			pass

def RANKS(): return [ "2", "3", "4", "5", "6", "7","8", "9", "T", "J", "Q", "K", "A" ]
def SUITS(): return [ "Clubs", "Diamonds", "Hearts", "Spades" ]
def HANDS(): return [ "HighCard", "Pair", "TwoPair", "Set", "Straight", "Flush", "FullHouse", "Quads", "StraighFlush", "RoyalFlush" ]

class Card:
	def __init__(self, rank, suit):
		self.rank = rank
		self.suit = suit
	def __eq__(self, other):
		return self.rank == other.rank and self.suit == other.suit

player_cards = [Card("2", "Clubs"), Card("3", "Spades")]
community_cards = [Card("2", "Diamonds"), Card("T", "Spades"), Card("3", "Spades"),  Card("T", "Diamonds")]
cards = player_cards + community_cards

hand, cards = HandRank(cards)

print(hand, [(card.rank, card.suit) for card in cards])
