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
from fractions import Fraction
from uuid import uuid1

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
		self.last_action = None
		self.debug_cards = debug_cards
		self.straddle = straddle
		self.flop_index = None
		self.position = None
		self.name = name
		self.stack = stack
		self.info = []
		self.starting_stack = stack.value
		self.hand_winnings = 0
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
		if any([p for p in hand.players if isinstance(p.curbet, int) and p.curbet >= self.stack.value]):
			options.remove("Raise")
		return options
	def BetPrompt(self, minbet):
		while True:
			try:
				betsize = int(input('%s, enter bet size %s-%s\n' % (self.name, minbet, self.stack.value)))
				if betsize < minbet or betsize > self.stack.value:
					raise ValueError
				return betsize
			except ValueError:
				print("Invalid integer. The number must be in the range of %s-%s." % (minbet, self.stack.value))
	def _bet(self, minbet=False, betsize=False):
		minbet = minbet - self.curbet
		if betsize is False: betsize = self.BetPrompt(minbet)
		## Action special definitions
		if betsize == self.stack.value: self.last_action = "AllIn"
		## Big and small blind "Post" the blinds
		if hand.street == 2 and (betsize == hand.small_blind or betsize == hand.small_blind*2) and self.index >= hand.start_players_n-2 and self.curbet == 0: self.last_action = "Post"
		if self.last_action == "Raise" and betsize == minbet: self.last_action = "MinRaise"
		TakeValue(self.stack, betsize)
		self.curbet = self.curbet + betsize
		# Need to trigger value change
		self.stack = self.stack
		#self.stack = self.stack - betsize
		main_pot = hand.pots[0]
		main_pot.Add((betsize), self.name)
		#hand.minbet = self.curbet
		betsize_in_hand_history = str(betsize) if self.last_action != "Check" else ""
		hand.history.append([StreetIdxToStreet(hand.street), self.name, self.last_action, betsize_in_hand_history, self.position])
		return self.curbet
	def Raise(self, *args, **kwargs):
		self.last_action = "Raise"
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
		betsize = self._bet(minbet=minbet)
		return betsize
	def Bet(self, minbet):
		self.last_action = "Bet"
		betsize = self._bet(minbet=minbet)
		return betsize
	def Check(self, minbet):
		self.last_action = "Check"
		return self._bet(minbet=minbet, betsize=0)
	def AllIn(self, minbet):
		self.last_action = "AllIn"
		return self._bet(minbet=minbet, betsize=self.stack.value)
	def Call(self, minbet):
		self.last_action = "Call"
		minbet = minbet - self.curbet
		betsize = minbet if minbet <= self.stack.value else self.stack.value 
		return self._bet(minbet=minbet, betsize=betsize)
	def Fold (self, *args, **kwargs):
		#hand.players.remove(self)
		self.last_action = "Fold"
		hand.history.append([StreetIdxToStreet(hand.street), self.name, "Fold", self.position])
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
	def __init__(self, debug=False):
		self.init = False
		self.id = str(uuid1().hex)
		self.history = []
		self.history.append(["Hand Id:", self.id])
		self.over = False
		self.completed = False
		self.betting = True
		self.debug = debug
		self.deck = Deck()
		self.pots = [Pot()]
		self.street = 2
		self.debug_board = ['J♥', 'T♥', '9♦', '7♠', 'T♠'] if debug == True else None
		self.small_blind = 10
		self._comcards = []
		self.folded_players = []
		self.winning_hands = []
		self.players = deque([ Player(*args, **kwargs) for args, kwargs in PLAYERS() ])
		# We need to know how many players were in the hand originally
		self.start_players_n = len(self.players)
		# If it's the first round, we need to randompy choose a dealer
		self.first_dealer_idx = list(self.players).index(np.random.choice(self.players, 1, replace=False)[0])
		# Static dealer for testing
		# Debug fixed dealer
		# self.first_dealer_idx = 1
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
		# Let's turn players into a list again to be able to remove items while looping - (not used anymore..)
		self.players = list(self.players)
		# Let's convert player indexes into table positions
		PopulatePositions(self.players)
		# The last player to act was the big blind, or straddle when we introduce it..
		# So we might change this to player with biggest bet etc
		self.last_player_to_act = False
	@property
	def comcards(self):
		return self._comcards
	@comcards.setter
	def comcards(self, cards):
		self._comcards = cards
		for p in self.players: p.GetHandRank()
	def DealOntable(self, number):
		self.comcards = [*self.comcards, *PickRandomCards(number)] if not self.debug_board else GetCardsfromPrintCards(self.debug_board[:(self.street)])
	def NewStreet(self):
		self.history.append(["New Street:", StreetIdxToStreet(self.street)])
		# Move foldeed players
		self.folded_players = self.folded_players + [p for p in self.players if p.curbet == 'Fold']
		# Remove folded players
		self.players = [p for p in self.players if not p.curbet == 'Fold']
		# At each street we need to clear the bets
		for p in self.players: p.curbet = 0
		# and set the minimum bet to the big blind again
		self.minbet = self.small_blind*2
		self.curbet = self.minbet
	def PlayerBettingOver(self):
		#Skip betting turn if player has folded or is all in 
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
		betting_players = list(set(self.players) - set(FoldedPlayers(self.players)) - set(AllinPlayers(self.players)))
		active_players = list(set(self.players) - set(FoldedPlayers(self.players)))
		if len(betting_players) > 1:
			self.betting = True
		elif len(betting_players) == 1:
			# Needed if all players are all-in preflop before the big blind, otherwise would skip it
			self.betting = False if betting_players[0].curbet >= self.curbet else True
		else:  
			self.betting = False
		# Note that betting might be over but we still need to go to showdown
		if not self.betting and len(active_players) == 1:
			self.over = True
			winning_player = next(filter(lambda p: p.curbet != 'Fold', self.players))
			for pot in self.pots:
				value_taken = TakeValueFromPot(pot, 1)
				winning_player.stack.value += value_taken
				winning_player.hand_winnings += value_taken
		PrintPotsDebug(self)
		pprint([(p.name, p.starting_stack, p.stack.value, (p.stack.value-p.starting_stack)) for p in self.players])
		return not self.betting
	def SkipBettingTurn(self, player):
		# Skip betting turn if player has folded or is all in 
		return True if (player.curbet == 'Fold' or player.stack.value == 0) else False
	def BettingRound(self):
		# Start betting round
		end = False
		while True:
			for idx, p in enumerate(self.players):
				# We need to start this at the playter after the last who acted
				# This won't be the case if we are resuming, in that case we go forward until that't true again
				if not self.last_player_to_act == self.players.index(self.players[self.players.index(p)-1]): continue
				if self.HandBettingOver():
					end = True
					break
				if self.SkipBettingTurn(p):
					# Skip if player has folded or is all in
					if self.StreetBettingOver(idx):
						end = True
						break
					continue
				PrintHistory(self.history)
				PrintPlayers(self)
				PrintPots(self)
				print("\n%s (You) %s\n" % (p.name, p.position))
				#print("Your Cards:", PrintCards(p.cards), "Your Hand:", p.hand['hand'], PrintCards(p.hand['cards']), "Strength:", p.hand['strength'])
				if hand.comcards: print("Board Cards:", PrintCardsAsString(hand.comcards))
				print("\n")
				# Debug everybody all-in
				# bet = getattr(p, 'AllIn')(minbet=self.minbet)
				player_options = p.GenOptions()
				# Let's give the player some info to decide
				p.info = []
				p.info.append("Your stack: $%s" % p.stack.value)
				if "Call" in player_options:
					to_call = ((self.minbet - p.curbet) if (self.minbet - p.curbet) < p.stack.value else p.stack.value)
					total_pots_value = GetTotalPotsValue(self.pots)
					stand_to_win = total_pots_value if total_pots_value < p.stack.value else p.stack.value  
					p.info.append("To Call: $%s" % to_call)
					p.info.append("Pot Odds: %s or %s" % ( round((to_call/stand_to_win),2), OddsToFraction((to_call/stand_to_win)) ) ) 
				p.info.append(' '.join([ "Your Cards:", ' '.join(PrintCards(p.cards)), "Your Hand:", p.hand['hand'] ]) )
				# Have to think minraise over
				#if "Raise" in player_options: p.info.append("Min Raise: $%s", % )
				PrintInfo(p.info)
				bet = getattr(p, Action(player_options))(minbet=self.minbet)
				if not p.curbet == "Fold":
					self.curbet = bet
					self.minbet = bet if bet > self.minbet else self.minbet
				# This is the point of save of the single player betting action
				self.last_player_to_act = self.players.index(p)
				PersistHand(self)
				if self.StreetBettingOver(idx):
					# We want to close the street and save the hand immediately after dealing the next table cards
					self.HandBettingOver()
					cards_to_deal = 3 if self.street == 2 else 1
					self.DealOntable(cards_to_deal)
					if self.street == 2: self.PositionPlayersForFlop()
					self.street +=1
					PersistHand(self)
					end = True
					break
				print("\n\n\n\n")
			if end: break
	def ShowDown(self):
		print("SHOWDOWN\n\n")
		for p in self.players: print(p.name, "CARDS", PrintCards(p.cards), "HAND", p.hand['hand'], PrintCards(p.hand['cards']), p.hand['strength'])
		print("BOARD", PrintCardsAsString(self.comcards))
		# Let's find if there are any ties
		# print(Counter([hand['strength'] for hand in [p.hand for p in self.players]]))
		# PrintPlayers(self)
		# PrintPotsDebug(self)
		active_players = ActivePlayers(self.players)
		ranked_unique_hands = sorted(list(set(p.hand['strength'] for p in active_players)), reverse=True)
		# PrintPotsDebug(self)
		for hand in ranked_unique_hands:
			hand_value = 0
			players_with_hand = ActivePlayersWithHand(self.players, hand)
			for pot in self.pots:
				# How many players with this hand have a stake in the pot?
				hand_players_in_pot = GetPlayersInPot(players_with_hand, pot)
				# We take our share, once taken we need decrease the share divisor
				share = len(hand_players_in_pot)
				# print(hand, self.pots.index(pot), [p.name for p in hand_players_in_pot])
				# If we are iterating, we are in the pot!
				for player in hand_players_in_pot:	
					# We get the value of the pot divided by the number of the hand_players in pot
					# print(player.name, "starting stack", player.starting_stack)
					value_taken = TakeValueFromPot(pot, share)
					# print(player.name, self.pots.index(pot), value_taken)
					# print("taken", value_taken, "from pot", self.pots.index(pot))
					player.stack.value += value_taken
					player.hand_winnings += value_taken
					hand_value += value_taken
					share -= 1
					# print(player.name, "new stack", player.stack.value)
			# Nothing more to take, we are done
			self.winning_hands += [GetHandCards(GetHandWithStrength(hand, active_players)), GetPlayerNames(players_with_hand), hand_value, [ (p.name, p.hand_winnings) for p in players_with_hand]]
			# log winning hands and value taken by players
			# Nothing more to take, we are done
			if not len(PotsWithValue(self.pots)): break
		PrintPotsDebug(self)
		pprint(self.winning_hands)
		pprint([(p.name, p.starting_stack, p.stack.value, (p.stack.value-p.starting_stack)) for p in self.players])
	def PositionPlayersForFlop(self):
		# Sort remaining players based on their flop_index, unless it's heads up and they need to be swapped
		if self.start_players_n > 2: 
			self.players.sort(key=lambda p: p.flop_index)
		else:
			self.players[0], self.players[1] = self.players[1], self.players[0]
	def DealCardsToPlayers(self):
		for p in self.players: 
			p.cards = GetCardsfromPrintCards(p.debug_cards) if (self.debug == True and p.debug_cards) else PickRandomCards(2)		
	def PreFlop(self):
		self.NewStreet()
		# Small and big blind, pay!
		# Do not pay again if Preflop is being resumed
		if not self.last_player_to_act:
			self.players[-2]._bet(betsize=self.small_blind)
			self.players[-1]._bet(betsize=self.small_blind*2)
			self.last_player_to_act = self.start_players_n-1
		# Start betting round
		self.BettingRound()
	def Flop(self):
		if self.over: return True
		self.NewStreet()
		if self.betting: self.BettingRound()
	def Turn(self):
		if self.over: return True
		self.NewStreet()
		if self.betting: self.BettingRound()
	def River(self):
		if self.over: return True
		self.NewStreet()
		if self.betting: self.BettingRound()
		self.ShowDown()
	# Streets are starting to look the same, we might want to generalize this
	def Run(self):
		#!! This code runs only the FIRST time the hand is run
		# We deal cards to players before saving the hand, if the hand during preflop betting, we want the cards to be the same
		if not self.init:
			self.DealCardsToPlayers()
			self.init = True
			PersistHand(self)
		for street in STREETS():
			# Skip completed streets if we are resuming
			if StreetNameToIdx(street) >= self.street: 
				getattr(self, street)()



# hand = Hand()
hand = LoadHand()
hand.Run()