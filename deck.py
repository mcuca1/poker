# Idea
# Hand lists wit ID and bets..cards and results
# Somehow map positions to poker names of positions and maybe area as well

import random
from random import shuffle
import numpy as np
from collections import deque
import inspect
from collections import defaultdict
from modules.hand_funcs import *
from modules.player_funcs import *

def PrintCards(cards):
	try: return [card.rank + card.suit for card in cards]
	except: return False

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
	return SortCardsByRank(list(cards))

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

class Card:
	def __init__(self, rank, suit):
		self.rank = rank
		self.suit = suit
	def __eq__(self, other):
		return self.rank == other.rank and self.suit == other.suit

class Deck:
	def __init__(self):
		self.contents = [ Card( rank, suit ) for rank in RANKS() for suit in SUITS() ]
	def Shuffle(self):
		random.shuffle(self.contents)
	def RemoveCard(self, card):
		self.contents.remove(card)

class Player(object):
	def __init__(self, name, stack):
		self.index = None
		self.flop_index = None
		self.position = None
		self.name = name
		self.stack = stack
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
		options.append("AllIn")
		# and they are in the same pot, which they wouldnt be if they went all in on flop with smaller stack
		if any([p for p in hand.players if isinstance(p.curbet, int) and p.curbet >= self.stack]):
			options.remove("Raise")
		return options
	def BetPrompt(self, minbet):
		while True:
			try:
				betsize = int(input('%s, enter bet size %s-%s\n' % (self.name, minbet, self.stack)))
				if betsize < minbet or betsize > self.stack:
					raise ValueError
				return betsize
			except ValueError:
				print("Invalid integer. The number must be in the range of %s-%s." % (minbet, self.stack))
	def Bet(self, minbet=False, betsize=False):
		minbet = minbet - self.curbet
		if betsize is False: betsize = self.BetPrompt(minbet)
		self.curbet = self.curbet + betsize
		self.stack = self.stack - betsize
		main_pot = hand.pots[0]
		main_pot.Add((betsize), self.name)
		#hand.minbet = self.curbet
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
	def AllIn(self, minbet):
		return self.Bet(minbet=minbet, betsize=self.stack)
	def Call(self, minbet):
		minbet = minbet - self.curbet
		betsize = minbet if minbet <= self.stack else self.stack 
		return self.Bet(minbet=minbet, betsize=betsize)
	def Fold (self, *args, **kwargs):
		#hand.players.remove(self)
		self.curbet = "Fold"


class Pot(object):
	def __init__(self):
		self.value = 0
		self.players_stakes = defaultdict(int)
		self.closed = False
	def Add(self, value, player):
		self.value = self.value + value
		self.players_stakes[player] += value 
		#self.players.append(player) if player not in self.players else self.players
	def Close(self):
		self.closed = True

class Hand(object):
	def __init__(self):
		self.over = False
		self.betting = True
		self.deck = Deck()
		self.pots = [Pot()]
		self.street = 1
		self.small_blind = 10
		self._comcards = []
		self.folded_players = []
		self.players = deque([ Player(name, stack) for (name, stack) in players ])
		# If it's the first round, we need to randompy choose a dealer
		self.first_dealer_idx = list(self.players).index(np.random.choice(self.players, 1, replace=False)[0])
		# Static dealer for testing
		self.first_dealer_idx = 1
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
		print("\n\n\n\n")
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
	def Over(self):
		if self.over:
			winning_player = next(filter(lambda p: p.curbet != 'Fold', self.players))
			winning_player.stack = winning_player.stack + self.pot
			self.pot = 0
			return True
	def PlayerBettingOver(self):
		# Skip betting turn if player has folded or is all in 
		return True if p.curbet == 'Fold' or p.stack == 0 else False
	def StreetBettingOver(self, idx):
		if self.street == 2: # PreFlop
			if (
				# All players have the same bet, hence the last has called closing the round
				all(p.curbet == self.curbet for p in list(set(self.players) - set(FoldedPlayers(self.players)) - set(AllinPlayers(self.players)))) and
				# We are not in the big blind on the next round. Preflop the big blind will have the same bet as everyone else, but still gets to decide what to do
				# This is the only instance when this happens in a hand
				not (idx == len(self.players)-2 and 
					self.curbet == self.small_blind*2) 
				): return True
		else: # Postflop
			if (
				# All players have the same bet, hence the last has called closing the round and it's not the start of a betting round when the current bet is zero 
				(all(p.curbet == self.curbet for p in list(set(self.players) - set(FoldedPlayers(self.players)) - set(AllinPlayers(self.players)))) and self.curbet !=0 ) or
				# All the players left in the hand have checked, the round is over
				(all(p.curbet == 0 for p in [p for p in self.players if isinstance(p.curbet, int)]) and 
					idx == len(self.players)-1)
				# 
				): return True
		return False
	def HandBettingOver(self):
		active_players = list(set(self.players) - set(FoldedPlayers(self.players)) - set(AllinPlayers(self.players)))
		if len(active_players) > 1:
			self.betting = True
		elif len(active_players) == 1:
			self.betting = False if active_players[0].curbet >= self.curbet else True
		else:
			self.betting = False
		return not self.betting
	def SkipBettingTurn(self, player):
		# Skip betting turn if player has folded or is all in 
		return True if (player.curbet == 'Fold' or player.stack == 0) else False
	def BettingRound(self):
		# Start betting round
		end = False
		while True:
			for idx, p in enumerate(self.players):
				if self.HandBettingOver(): 
					end = True
					break
				if self.SkipBettingTurn(p):
					if self.StreetBettingOver(idx):
						end = True
						break
					continue
				print(p.index, "PL", p.name, "CUR", p.curbet, "IDX", "("+ p.position + ")")
				print("BEFORE", "BETS", [p.curbet for p in self.players], "STACKS", [p.stack for p in self.players])
				print(p.name, "CARDS", PrintCards(p.cards), "HAND", p.hand[0], PrintCards(p.hand[1]))
				print("BOARD", PrintCards(self.comcards))
				print("YOUR STACK:", p.stack)
				print("TO CALL", ((self.minbet - p.curbet) if (self.minbet - p.curbet) < p.stack else p.stack))
				# For the love or god do not use idx here
				for potidx, pot in enumerate(self.pots):
					print("POT_%s:" % potidx, pot.value, dict(pot.players_stakes))
				
				bet = getattr(p, Action(p.GenOptions()))(minbet=self.minbet)
				
				if not p.curbet == "Fold": 
					self.curbet = bet
					self.minbet = bet if bet > self.minbet else self.minbet

				print([(p.curbet, p.name) for p in self.players])
				print(idx, len(self.players), self.curbet)
				if self.StreetBettingOver(idx):
					self.HandBettingOver()
					end = True
					break
				print("\n\n\n\n")
			if end: break
	def ShowDown(self):
		print("SHOWDOWN")
		for p in self.players: print(p.name, "CARDS", PrintCards(p.cards), "HAND", p.hand[0], PrintCards(p.hand[1]))
		print("BOARD", PrintCards(self.comcards))
	def PreFlop(self):
		self.NewStreet()
		# Let's deal the cards to each player
		for p in self.players: p.cards = PickRandomCards(2)
		# Small and big blind, pay!
		self.players[-2].Bet(betsize=self.small_blind)
		self.players[-1].Bet(betsize=self.small_blind*2)
		# Start betting round
		self.BettingRound()
		return True if self.Over() else False
	def Flop(self):
		if self.Over(): return False
		self.NewStreet()
		# Sort remaining players based on their flop_index
		self.players.sort(key=lambda p: p.flop_index)
		self.DealOntable(3)
		if self.betting: self.BettingRound()
		return True if self.Over() else False
	def Turn(self):
		if self.Over(): return False
		self.NewStreet()
		self.DealOntable(1)
		if self.betting: self.BettingRound()
		return True if self.Over() else False
	def River(self):
		if self.Over(): return False
		self.NewStreet()
		self.DealOntable(1)
		if self.betting: self.BettingRound()
		self.ShowDown()
	

players =  [('Player1', 10000), ('Player2', 2000), ('Player3', 500), ('Player4', 100)]
streets = ['PreFlop', 'Flop', 'Turn', 'River']
hand = Hand()

for p in hand.players: print(p.name, p.position, p.index, p.flop_index)

for street in streets:
	print('##########', street)
	if getattr(hand, street)():
		for p in hand.players: print(p.name, p.stack, p.curbet, p.position)
		for p in hand.folded_players: print(p.name, p.stack, p.curbet, p.position)
	for potidx, pot in enumerate(hand.pots):
		print("POT_%s:" % potidx, pot.value, dict(pot.players_stakes))