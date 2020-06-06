from pprint import pprint
from modules.helper_funcs import *

def PLAYERS(): 
	players = [	(['Player0', 500], {'debug_cards': ['6♣', '2♦']}), 
				(['Player1', 750], {'debug_cards': ['8♥', '5♣']}), 
				(['Player2', 800], {'debug_cards': ['8♣', '2♠']}), 
				(['Player3', 850], {'debug_cards': ['7♦', '2♣']}),
				(['Player4', 2000], {'debug_cards': ['8♣', '2♠']}), 
				(['Player5', 1500], {'debug_cards': ['7♦', '2♣']})
				]
	return [([p[0][0], ValueContainer(p[0][1])], p[1]) for p in players]

def PopulatePositions(players):
	number_of_players = len(players)
	positions = []
	if number_of_players > 2:
		positions.append(dict([
		(0, 'UTG  '),
		(1, 'UTG+1'),
		(2, 'UTG+2'),
		(3, 'UTG+3'),
		(4, 'UTG+4'),
		(5, 'UTG+5'),
		(6, '7th  '),
		(7, '8th  '),
		(8, '9th  '),
		(9, '10th '),
		(number_of_players-1, 'Big Blind  '),
		(number_of_players-2, 'Small Blind'),
		(number_of_players-3, 'Dealer     '),
		(number_of_players-4, 'CutOff     '),
		(number_of_players-5, 'HiJack     '),
		]))
	if number_of_players > 4 and number_of_players <=6:
		positions.append(dict([
		(0, 'UTG '),
		(1, 'UTG+1')
		]))
	if number_of_players > 2 and number_of_players <=4:
		positions.append(dict([
		(0, 'UTG ')
		]))		
	if number_of_players == 2:
		positions.append(dict([
		(1, 'Big Blind'),
		(0, 'Dealer/SmallBlind')
		]))
	for player in players:
		for pos_dict in positions:
			try:		
				player.position = pos_dict[player.index]
			except:
				pass

def FoldedPlayers(players):
	return [p for p in players if p.curbet == 'Fold']

def AllinPlayers(players):
	return [p for p in players if p.stack.value == 0 and p.curbet != 'Fold']

def ActivePlayers(players):
	return list(set(players) - set(FoldedPlayers(players)))

def MyPots(player, pots):
	return [pot for pot in pots if player.name in pot.players_stakes.keys()]

def GetPotStakes(pot):
	stakes = []
	for player, stake in pot.players_stakes.items():
		stakes.append((player, stake.value))
	return stakes

def CleanPotStakes(pot):
	# Removes a player from a pot if his stake is zero, this 
	# is needed if the big blind goes all in witha smaller stack
	# than a previous all-in, for example
	players_to_remove = []
	for player, stake in pot.players_stakes.items():
		if stake.value == 0: players_to_remove.append(player)
	for player in players_to_remove: del pot.players_stakes[player]

def PrintCards(cards):
	try: return [card.rank + card.suit for card in cards]
	except: return False

def PrintCardsAsString(cards):
	try: return ' '.join([card.rank + card.suit for card in cards])
	except: return False

def PrintPlayers(hand):
	pprint([(p.name, "$"+str(p.stack.value), "$"+str(p.curbet), p.position) for p in hand.players ])
	print("\n")

def PrintPots(hand):
	for pot in hand.pots:
		print("POT N"+str(hand.pots.index(pot)+1)+" =", "$"+str(pot.value))

def PrintPotsDebug(hand):
	for pot in hand.pots:
		print(hand.pots.index(pot), pot.value, GetPotStakes(pot), pot.MAX)

def ActivePlayersWithHand(players, hand):
	return [p for p in players if p.hand['strength'] == hand]

def GetPlayersInPot(players, pot):
	return [p for p in players if p.name in pot.players_stakes.keys()]

def GetHandWithStrength(strength, players):
	return next(iter([p.hand for p in players if p.hand['strength'] == strength ]))

def GetPlayerNames(players):
	return [p.name for p in players]