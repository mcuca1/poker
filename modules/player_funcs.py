def FoldedPlayers(players):
	return [p for p in players if p.curbet == 'Fold']

def AllinPlayers(players):
	return [p for p in players if p.stack == 0 and p.curbet != 'Fold']

def MyPots(player, pots):
	return [pot for pot in pots if player.name in pot.players_stakes.keys()]

def TakeValue(bet, value):
	bet.value = bet.value - value
	return value

def GetPotStakes(pot):
	stakes = []
	for player, valuecontainer in pot.players_stakes.items():
		stakes.append((player, valuecontainer.value))
	return stakes