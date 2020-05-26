# Idea
# Hand lists wit ID and bets..cards and results
# Somehow map positions to poker names of positions and maybe area as well

import random
from random import shuffle
import numpy as np
from collections import deque
 
def PickRandomCards(number, deck):
	cards = np.random.choice(deck.contents, number, replace=False)
	for card in cards:
		deck.RemoveCard(card)
	return cards

def Action(options):
	while True:
		print("Action:")
		for idx, element in enumerate(options):
			print("{}) {}".format(idx+1,element))
		i = input("Enter number: ")
		try:
			if 0 < int(i) <= len(options):
				return options[int(i)-1]
			else:
				continue
		except:
			continue

def RANKS(): return [ "A", "2", "3", "4", "5", "6", "7","8", "9", "T", "J", "Q", "K" ]
def SUITS(): return [ "Clubs", "Diamonds", "Hearts", "Spades" ]

class Card:
	def __init__(self, rank, suit):
		self.rank = rank
		self.suit = suit
	def __eq__(self, other):
		return self.rank == other.rank and self.suit == other.suit

class Deck:
	def __init__(self):
		self.contents = []
		self.contents = [ Card( rank, suit ) for rank in RANKS() for suit in SUITS() ]
	def Shuffle(self):
		random.shuffle(self.contents)
	def RemoveCard(self, card):
		self.contents.remove(card)

class Player:
	def __init__(self, name):
		self.index = None
		self.name = name
		self.stack = 1500
		self.curbet = 0
		self.cards = False
		self.isdealer = False
		#self.options = ['Fold', 'Check', 'Bet', 'Call']
	def GenOptions(self):
		options = []
		# You can always fold
		options.append("Fold")
		# Let's differentiate between call, raise and check, bet
		# You call if there is a bet which is higher than you current bet
		if any(p.curbet > self.curbet for p in [p for p in hand.players if isinstance(p.curbet, int)]):
			options.append("Call")
			options.append("Raise")
		else:
			options.append("Check")
			options.append("Bet")
		return options
	def BetPrompt(self, minbet):
		while True:
			try:
				betsize = int(input('%s, enter bet size %s-%s\n' % (self.name, minbet, self.stack)))
				if betsize < minbet or betsize > self.stack:
					raise ValueError
				return betsize
			except ValueError:
				print("Invalid integer. The number must be in the range of %s-%s." % (minbet.size, self.stack))
	def Bet(self, minbet=False, betsize=False):
		minbet = minbet - self.curbet
		if betsize is False: betsize = self.BetPrompt(minbet)  
		self.curbet = self.curbet + betsize
		self.stack = self.stack - betsize
		hand.pot = hand.pot + betsize
		hand.minbet = self.curbet
		return self.curbet
	def Raise(self, *args, **kwargs):
		# Let's get all the bets in the current session, and sort them by size:
		bets = sorted(list(set([p.curbet for p in hand.players if isinstance(p.curbet, int)])), reverse=True)
		# Min raise is twice the difference betweem the larger and second larger bet, adding self.curbet as it's going to be subtracted
		minbet = bets[0]+(bets[0]-bets[1])
		# Only exception is the first raise preflop that has to be at least 2*BB
		if bets[0] == 2*hand.small_blind: minbet = 4*hand.small_blind
		return self.Bet(minbet=minbet)
	def Check(self, minbet):
		return self.Call(minbet=minbet)
	def Call(self, minbet):
		minbet = minbet - self.curbet
		print("Call", minbet)
		return self.Bet(minbet=minbet, betsize=minbet)
	def Fold (self, *args, **kwargs):
		#hand.players.remove(self)
		self.curbet = "Fold"

class Hand:
	def __init__(self):
		self.deck = Deck()
		self.pot = 0
		self.small_blind = 10
		self.minbet = self.small_blind*2
		self.curbet = self.minbet
		self.table_cards = []
		self.players = deque([ Player(i) for i in players ])
		# If it's the first round, we need to randompy choose a dealer
		self.first_dealer_idx = list(self.players).index(np.random.choice(self.players, 1, replace=False)[0])
		self.players[self.first_dealer_idx].isdealer = True
		# Now let's rotate the players so that the dealer is in position -3
		rotate = ((len(self.players)-self.first_dealer_idx)-3)
		# Get the index of the dealer according to number of players
		self.dealer_idx = (len(self.players)-1)-2
		self.players.rotate(rotate)
		# Let's turn players into a list again to be able to remove items while looping
		self.players = list(self.players)
		# Lets write the initial index inside the players so that we never loose track of what the inital positions were
		for idx, p in enumerate(self.players): p.index = idx
		# Let's deal the cards to each player
		for p in self.players: p.cards = PickRandomCards(2, self.deck)
	def Preflop(self):
		# Small and big blind, pay!
		self.players[-2].Bet(betsize=self.small_blind)
		self.players[-1].Bet(betsize=self.small_blind*2)
		# Start betting round
		# 1st player to dealer
		while True:
			for idx, p in enumerate(self.players):
				# Skip if has folded
				if p.curbet == 'Fold':
					continue
				print("PL", p.name, "CUR", p.curbet, "IDX", p.index)
				print("BEFORE", [p.curbet for p in self.players])
				bet = getattr(p, Action(p.GenOptions()))(minbet=self.minbet)
				if not p.curbet == "Fold": self.curbet = bet
				#curbet = p.Bet(minbet=self.minbet)
				print([p.curbet for p in self.players])
				print(idx, len(self.players), self.curbet)
				end = True if all(p.curbet == self.curbet for p in [p for p in self.players if isinstance(p.curbet, int)]) and not (idx == len(self.players)-2 and self.curbet == self.small_blind*2) else False
				if end: break
			if end: break



players =  ['A', 'B', 'C', 'D']

hand = Hand()
hand.Preflop()
for p in hand.players: print(p.name, p.stack, p.curbet)