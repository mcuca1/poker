def TakeValue(fromthis, thismuch):
	if fromthis.value > thismuch:
		fromthis.value = fromthis.value - thismuch
		# Return what you've taken
		return thismuch
	else:
		# There isn't enough, take what's in there
		thismuch = fromthis.value
		fromthis.value = 0
		return thismuch

def reverse_enumerate(L):
	# Only works on things that have a len()
	l = len(L)
	for i, n in enumerate(L):
		yield l-i-1, n

class ValueContainer(object):
	def __init__(self, value):
		self.value = value

def PotsWithValue(pots):
	return [pot for pot in pots if pot.value > 0]

def TakeValueFromPot(pot, portion):
	from modules.player_funcs import ValueContainer
	return sum([TakeValue(stake, (stake.value/portion)) for stake in pot.players_stakes.values()])

def GetHandCards(hand):
	return [card.rank + card.suit for card in hand['cards']]