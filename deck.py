# Idea
# Hand lists wit ID and bets..cards and results
# Somehow map positions to poker names of positions and maybe area as well

import random
from random import shuffle
import numpy as np
from collections import deque
import inspect

def HandRank(cards):
	def sort_cards_by_rank(cards):
		rankdict = dict([(t[1], t[0]) for t in list(enumerate(RANKS()))])
		cards.sort(key=lambda x: rankdict[x.rank], reverse=True)
		return cards
	return ('whoknows', sort_cards_by_rank(cards))

def PrintCards(cards):
	return [(card.rank, card.suit) for card in cards]

def PopulatePositions(players):
	number_of_players = len(players)
	positions = []
	if number_of_players > 2:
		positions.append(dict([
		(0, 'UTG'),
		(1, 'UTG+1'),
		(2, 'UTG+2'),
		(3, 'UTG+3'),
		(4, 'UTG+4'),
		(5, 'UTG+5'),
		(6, '7th'),
		(7, '8th'),
		(8, '9th'),
		(9, '10th'),
		(number_of_players-1, 'Big Blind'),
		(number_of_players-2, 'Small Blind'),
		(number_of_players-3, 'Dealer'),
		(number_of_players-4, 'CutOff'),
		(number_of_players-5, 'HiJack'),
		]))
	if number_of_players > 4 and number_of_players <=6:
		positions.append(dict([
		(0, 'UTG'),
		(1, 'UTG+1')
		]))
	if number_of_players > 2 and number_of_players <=4:
		positions.append(dict([
		(0, 'UTG')
		]))		
	if number_of_players == 2:
		positions.append(dict([
		(-0, 'Small Blind'),
		(-1, 'Dealer')
		]))
	for player in players:
		for pos_dict in positions:
			try:
				player.position = pos_dict[player.index]
			except:
				pass

def MapStreet(idx):
	streets = dict([(2,'PreFlop'),(3,'Flop'),(4,'Turn'),(5,'River')])
	return streets[idx]

def PickRandomCards(number):
	cards = np.random.choice(hand.deck.contents, number, replace=False)
	for card in cards:
		hand.deck.RemoveCard(card)
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

def RANKS(): return [ "2", "3", "4", "5", "6", "7","8", "9", "T", "J", "Q", "K", "A" ]
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

class Player(object):
	def __init__(self, name):
		self.index = None
		self.flop_index = None
		self.position = None
		self.name = name
		self.stack = 1500
		self.curbet = 0
		self._cards = None
		self.hand = None
		self.isdealer = False
	def GetHandRank(self):
		self.hand = HandRank([x for x in self.cards] + [x for x in hand.comcards])
	@property
	def cards(self):
		return self._cards
	@cards.setter
	def cards(self, cards):
		self._cards = cards
		self.GetHandRank()
	def GenOptions(self):
		options = []
		# You can always fold
		options.append("Fold")
		# Let's differentiate between call, raise and check, bet
		# You call if there is a bet which is higher than you current bet
		if any(p.curbet > self.curbet for p in [p for p in hand.players if isinstance(p.curbet, int)]):
			options.append("Call")
			options.append("Raise")
		elif hand.street == 2 and self.curbet == hand.small_blind*2:
			options.append("Check")
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
		# Big blind preflop is a raise if everybody called, but would break as there  is no smaller bet
		try:
			bets[1]
		except IndexError:
			bets.append(0)
		# Min raise is twice the difference betweem the larger and second larger bet, adding self.curbet as it's going to be subtracted
		minbet = bets[0]+(bets[0]-bets[1])
		# Only exception is the first raise preflop that has to be at least 2*BB
		if bets[0] == 2*hand.small_blind: minbet = 4*hand.small_blind
		return self.Bet(minbet=minbet)
	def Check(self, minbet):
		return self.Bet(minbet=minbet, betsize=0)
	def Call(self, minbet):
		minbet = minbet - self.curbet
		print("Call", minbet)
		return self.Bet(minbet=minbet, betsize=minbet)
	def Fold (self, *args, **kwargs):
		#hand.players.remove(self)
		self.curbet = "Fold"

class Hand(object):
	def __init__(self):
		self.over = False
		self.deck = Deck()
		self.pot = 0
		self.street = 1
		self.small_blind = 10
		self._comcards = []
		self.folded_players = []
		self.players = deque([ Player(i) for i in players ])
		# If it's the first round, we need to randompy choose a dealer
		self.first_dealer_idx = list(self.players).index(np.random.choice(self.players, 1, replace=False)[0])
		self.players[self.first_dealer_idx].isdealer = True
		# Now let's rotate the players so that the dealer is in position -3
		rotate = ((len(self.players)-self.first_dealer_idx)-3)
		self.players.rotate(rotate)
		# Lets write the initial index inside the players so that we never loose track of what the inital positions were
		for idx, p in enumerate(self.players): p.index = idx
		# Lets rotate the players again to get the order they play on the flop onwards
		self.players.rotate(2)
		for idx, p in enumerate(self.players): p.flop_index = idx
		# Lets reposition the players
		self.players.rotate(-2)
		# Let's turn players into a list again to be able to remove items while looping
		self.players = list(self.players)
		# Let's convert player indexes into table positions
		PopulatePositions(self.players)
	@property
	def comcards(self):
		return self._comcards
	@comcards.setter
	def comcards(self, cards):
		self._comcards = cards
		for p in self.players: p.GetHandRank()
	def DealOntable(self, number):
		self.comcards = [*self.comcards, *PickRandomCards(number)]
	def NewStreet(self):
		self.street +=1
		print("STREET:", MapStreet(self.street))
		# Move foldeed players
		self.folded_players = self.folded_players + [p for p in self.players if p.curbet == 'Fold']
		# Remove folded players
		self.players = [p for p in self.players if not p.curbet == 'Fold']
		# At each street we need to clear the bets
		for p in self.players: p.curbet = 0
		# and set the minimum bet to the big blind again
		self.minbet = self.small_blind*2
		self.curbet = self.minbet
	def IsItOver(self):
		if self.over:
			winning_player = next(filter(lambda p: p.curbet != 'Fold', self.players))
			winning_player.stack = winning_player.stack + self.pot
			self.pot = 0
			return True
	def BettingRound(self):
		# Start betting round
		while True:
			for idx, p in enumerate(self.players):
				# End if all players but this one have folded
				if len([p for p in self.players if isinstance(p.curbet, int)]) == 1:
					end = True
					self.over = True
					break
				# Skip if has folded
				if p.curbet == 'Fold':
					continue
				print(p.index, "PL", p.name, "CUR", p.curbet, "IDX", p.position)
				print("BEFORE", [p.curbet for p in self.players])
				print(p.name, "CARDS", PrintCards(p.cards), "HAND", p.hand[0], PrintCards(p.hand[1]))
				print("BOARD", [[card.rank, card.suit] for card in self.comcards])
				bet = getattr(p, Action(p.GenOptions()))(minbet=self.minbet)
				if not p.curbet == "Fold": self.curbet = bet
				#curbet = p.Bet(minbet=self.minbet)
				print([(p.curbet, p.position) for p in self.players])
				print(idx, len(self.players), self.curbet)
				if self.street == 2: # PreFlop
					end = True if all(p.curbet == self.curbet for p in [p for p in self.players if isinstance(p.curbet, int)]) and not (idx == len(self.players)-2 and self.curbet == self.small_blind*2) else False
				else:
					end = True if (all(p.curbet == self.curbet for p in [p for p in self.players if isinstance(p.curbet, int)]) and self.curbet !=0 ) or (all(p.curbet == 0 for p in [p for p in self.players if isinstance(p.curbet, int)]) and idx == len(self.players)-1) else False
				if end: break
			if end: break
	def PreFlop(self):
		self.NewStreet()
		# Let's deal the cards to each player
		for p in self.players: p.cards = PickRandomCards(2)
		# Small and big blind, pay!
		self.players[-2].Bet(betsize=self.small_blind)
		self.players[-1].Bet(betsize=self.small_blind*2)
		# Start betting round
		self.BettingRound()
		return True if self.IsItOver() else False
	def Flop(self):
		if self.IsItOver(): return False
		self.NewStreet()
		# Sort remaining players based on their flop_index
		self.players.sort(key=lambda p: p.flop_index)
		self.DealOntable(3)
		self.BettingRound()
		return True if self.IsItOver() else False
	def Turn(self):
		if self.IsItOver(): return False
		self.NewStreet()
		self.DealOntable(1)
		self.BettingRound()
		return True if self.IsItOver() else False
	def River(self):
		if self.IsItOver(): return False
		self.NewStreet()
		self.DealOntable(1)
		self.BettingRound()
	

players =  ['A', 'B', 'C', 'D']
streets = ['PreFlop', 'Flop', 'Turn', 'River']
hand = Hand()

for p in hand.players: print(p.name, p.position, p.index, p.flop_index)

for street in streets:
	print('##########', street)
	if getattr(hand, street)():
		for p in hand.players: print(p.name, p.stack, p.curbet, p.position)
		for p in hand.folded_players: print(p.name, p.stack, p.curbet, p.position)
	print("POT", hand.pot)