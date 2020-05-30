def FoldedPlayers(players):
	return [p for p in players if p.curbet == 'Fold']

def AllinPlayers(players):
	return [p for p in players if p.stack == 0 and p.curbet != 'Fold']

def MyPots(player, pots):
	return [pot for pot in pots if player.name in pot.players_stakes.keys()]

def TakeValue(bet, value):
	if bet.value > value:
		bet.value = bet.value - value
		return value
	else:
		value = bet.value
		bet.value = 0
		return value

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