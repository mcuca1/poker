def FoldedPlayers(players):
	return [p for p in players if p.curbet == 'Fold']

def AllinPlayers(players):
	return [p for p in players if p.stack == 0 and p.curbet != 'Fold']

def MyPots(player, pots):
	return [pot for pot in pots if player.name in pot.players_stakes.keys()]