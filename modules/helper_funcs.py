
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

def TakeValueFromPot(pot):
	from modules.player_funcs import ValueContainer
	return sum([TakeValue(stake.value) for stake in pot.players_stakes.values()])