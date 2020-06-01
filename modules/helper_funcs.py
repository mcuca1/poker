import os, pickle, glob

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

def GetCardsfromPrintCards(printcards):
	from modules.hand_funcs import Card
	return [ Card(card[0], card[1]) for card in printcards ]

def PrintInfo(info):
	for line in info:
		print("Info: " + line)
	print("\n")

def PrintHistory(history):
	print("\n")
	for entry in history:
		line = "Hand History:  " + ' '.join([str(x) for x in entry])
		print(line)
	print("\n")

def GetTotalPotsValue(pots):
	return sum([pot.value for pot in pots])


def OddsToFraction(odds):
	fraction = odds.as_integer_ratio()
	denominator = fraction[1]/fraction[0]
	return "one in %s" % round(denominator, 1)

def StreetIdxToStreet(idx):
	streetsdict = {
	2: 'PreFlop',
	3: 'Flop',
	4: 'Turn',
	5: 'River'
	}
	return streetsdict[idx]

def StreetNameToIdx(name):
	streetsdict = {
	2: 'PreFlop',
	3: 'Flop',
	4: 'Turn',
	5: 'River'
	}
	reversstreetsdict = dict((v,k) for k,v in streetsdict.items())
	return reversstreetsdict[name]

def PersistHand(hand):
	#curdir = os.path.dirname(os.path.realpath(__file__))
	hand_filepath = os.path.join("C:\\Users\\marco\\Documents\\GitHub\\poker", "hands", hand.id)
	with open(hand_filepath, 'wb') as hand_file:
		pickle.dump(hand, hand_file)
	hand_file.close()

def LoadHand(hand_id=None):
	#curdir = os.path.dirname(os.path.realpath(__file__))
	rootdir = "C:\\Users\\marco\\Documents\\GitHub\\poker"
	if hand_id:
		hand_filepath = os.path.join(rootdir, "hands", hand_id)
	else:
		latest_saved_hand = max(glob.glob(os.path.join(rootdir, "hands", "*")), key=os.path.getctime)
		hand_filepath = latest_saved_hand
	with open(hand_filepath, 'rb') as hand_file:
		hand = pickle.load(hand_file)
	return hand

