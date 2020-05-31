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
from pprint import pprint

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
				return options[int(i)  -1]
			else:
				continue
		except:
			continue

class Player(object):
	@property
	def stack(self):
		return self._stack
	@stack.setter
	def stack(self, stack):
		self._stack = stack
		# The stack is updated at every bet, if the stack becomes zero, the player is all in
		# And we need to lock the pot to his last bet size
		if self._stack.value == 0: 
			hand.pots[0].SetMax(self.curbet)
	def __init__(self, name, stack, straddle=0, debug_cards=None):
		self.index = None
		self.debug_cards = debug_cards
		self.straddle = straddle
		self.flop_index = None
		self.position = None
		self.name = name
		self.stack = stack
		self.starting_stack = stack.value
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
		TakeValue(self.stack, betsize)
		# Need to trigger value change
		self.stack = self.stack
		#self.stack = self.stack - betsize
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
		return self.Bet(minbet=minbet, betsize=self.stack.value)
	def Call(self, minbet):
		minbet = minbet - self.curbet
		betsize = minbet if minbet <= self.stack.value else self.stack.value 
		return self.Bet(minbet=minbet, betsize=betsize)
	def Fold (self, *args, **kwargs):
		#hand.players.remove(self)
		self.curbet = "Fold"

class StakesDict(defaultdict):
    def __missing__(self, key):
        self[key] = value = ValueContainer(0)
        return value

class Pot(object):
	def __init__(self, MAX=float("inf")):
		self.players_stakes = StakesDict()
		self.MAX = MAX
	@property
	def value(self):
		return sum([x.value for x in self.players_stakes.values()])
	def SetMax(self, MAX):
		if not self.MAX == float("inf"):
			if MAX >= self.MAX:
				try:
					next_pot = hand.pots[hand.pots.index(self)+1]
				except IndexError:
					hand.pots.append(Pot())
					next_pot = hand.pots[hand.pots.index(self)+1]
				next_pot.SetMax(MAX-self.MAX)
			else:
				new_pot_index = hand.pots.index(self)
				hand.pots.insert(new_pot_index, Pot(MAX=MAX))
				# print(GetPotStakes(hand.pots[new_pot_index+1]))
				for player, potstake in hand.pots[new_pot_index+1].players_stakes.items():
					hand.pots[new_pot_index].players_stakes[player].value += TakeValue(potstake, MAX)
				CleanPotStakes(hand.pots[new_pot_index+1])
				self.MAX = self.MAX - MAX
		else:
			self.MAX = MAX
	def Add(self, value, player):
		if value <= self.MAX:
			self.players_stakes[player].value += value
		else:
			bet = ValueContainer(value)
			player_max = self.MAX - self.players_stakes[player].value
			pot_max = TakeValue(bet, player_max)
			self.players_stakes[player].value += pot_max	
			if bet.value > 0:
				next_pot = hand.pots[hand.pots.index(self)+1]
				next_pot.Add(bet.value, player)

class Hand(object):
	def __init__(self):
		self.over = False
		self.betting = True
		self.deck = Deck()
		self.pots = [Pot()]
		self.street = 1
		self.debug_board = ['J♥', 'T♥', '9♦', '7♠', 'T♠']
		self.small_blind = 10
		self._comcards = []
		self.folded_players = []
		self.winning_hands = []
		self.players = deque([ Player(*args, **kwargs) for args, kwargs in PLAYERS() ])
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
		self.comcards = [*self.comcards, *PickRandomCards(number)] if not self.debug_board else self.comcards + GetCardsfromPrintCards(self.debug_board[:number])
	def NewStreet(self):
		self.street +=1
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
		return True if p.curbet == 'Fold' or p.stack.value == 0 else False
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
		return True if (player.curbet == 'Fold' or player.stack.value == 0) else False
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
				PrintPlayers(self)
				PrintPots(self)
				print("\n%s (You) %s\n" % (p.name, p.position))
				print("Your Cards:", PrintCards(p.cards), "Your Hand:", p.hand['hand'], PrintCards(p.hand['cards']), "Strength:", p.hand['strength'])
				if hand.comcards: print("Board Cards:", PrintCards(hand.comcards))
				print("\n")
				bet = getattr(p, 'AllIn')(minbet=self.minbet)
				#bet = getattr(p, Action(p.GenOptions()))(minbet=self.minbet)
				if not p.curbet == "Fold": 
					self.curbet = bet
					self.minbet = bet if bet > self.minbet else self.minbet
				if self.StreetBettingOver(idx):
					self.HandBettingOver()
					end = True
					break
				print("\n\n\n\n")
			if end: break
	def ShowDown(self):
		print("SHOWDOWN\n\n")
		for p in self.players: print(p.name, "CARDS", PrintCards(p.cards), "HAND", p.hand['hand'], PrintCards(p.hand['cards']), p.hand['strength'])
		print("BOARD", PrintCards(self.comcards))
		# Let's find if there are any ties
		# print(Counter([hand['strength'] for hand in [p.hand for p in self.players]]))
		# PrintPlayers(self)
		# PrintPotsDebug(self)
		active_players = ActivePlayers(self.players)
		ranked_unique_hands = sorted(list(set(p.hand['strength'] for p in active_players)), reverse=True)
		for hand in ranked_unique_hands:
			hand_value = 0
			players_with_hand = ActivePlayersWithHand(self.players, hand)
			for pot in self.pots:
				# How many players with this hand have a stake in the pot?
				hand_players_in_pot = GetPlayersInPot(players_with_hand, pot)
				# print(hand, self.pots.index(pot), [p.name for p in hand_players_in_pot])
				# If we are iterating, we are in the pot!
				for player in hand_players_in_pot:	
					# We get the value of the pot divided by the number of the hand_players in pot
					# print(player.name, "starting stack", player.starting_stack)
					value_taken = TakeValueFromPot(pot, len(hand_players_in_pot))
					# print("taken", value_taken, "from pot", self.pots.index(pot))
					player.stack.value += value_taken
					hand_value += value_taken
					# print(player.name, "new stack", player.stack.value)
			# Nothing more to take, we are done
			self.winning_hands.append( (GetHandCards(GetHandWithStrength(hand, active_players)), GetPlayerNames(players_with_hand), hand_value) )
			# log winning hands and value taken by players
			# Nothing more to take, we are done
			if not len(PotsWithValue(self.pots)): break
		PrintPotsDebug(self)
		# print("Pots with Value", PotsWithValue(self.pots))
		pprint(self.winning_hands)

	def PreFlop(self):
		self.NewStreet()
		# Let's deal the cards to each player
		for p in self.players: 
			p.cards = PickRandomCards(2) if not p.debug_cards else GetCardsfromPrintCards(p.debug_cards)
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
	def Start(self):	
		for street in STREETS():
			getattr(self, street)()

hand = Hand()
hand.Start()