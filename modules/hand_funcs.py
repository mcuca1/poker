from collections import deque
from collections import Counter
from modules.helper_funcs import *

def RANKS(acehigh=True): 
	RANKS = deque([ "2", "3", "4", "5", "6", "7","8", "9", "T", "J", "Q", "K", "A" ])
	if acehigh: return list(RANKS)
	RANKS.rotate(1)
	return list(RANKS)
def SUITS(): return [ "♣", "♦", "♥", "♠" ]
def HANDS(): return [ "HighCard", "Pair", "TwoPair", "Set", "Straight", "Flush", "FullHouse", "Quads", "StraightFlush", "RoyalFlush" ]
def ranks_to_rankdict(ranks):
	# rankdict to be used for sorting
	return dict([(t[1], t[0]) for t in list(enumerate(ranks))])
def SortUniqueRanks(cards, rankdict=ranks_to_rankdict(RANKS())):
	ranks = set(list([card.rank for card in cards]))
	return sorted(ranks, key=lambda x: rankdict[x], reverse=True)
def SortCardsByRank(cards, rankdict=ranks_to_rankdict(RANKS())):
	cards.sort(key=lambda x: rankdict[x.rank], reverse=True)
	return cards
def GetRankHandRanks(cards, n):
	ranks = []
	for rank in SortUniqueRanks(cards):
		if sum(card.rank == rank for card in cards) == n: ranks.append(rank)
	return ranks
# Pairs, sets and quads are one rank hands, changing only the number of cards
def OneRankHand(cards, n):
	# Kickers are the best cards left between the hand and the total 5
	kickers = 5 - n
	# Return highest pair + highest kickers
	rankhand_ranks = GetRankHandRanks(cards, n)
	if len(rankhand_ranks) == 0: return []
	highest_rankhand = [card for card in cards if card.rank in rankhand_ranks[0]]
	for card in highest_rankhand: cards.remove(card)
	cards = SortCardsByRank(cards)[:kickers]
	return highest_rankhand + cards
def GetStraightRanks(cards):
	sorted_ranks, sorted_ranks_acelow = SortUniqueRanks(cards), SortUniqueRanks(cards, rankdict=ranks_to_rankdict(RANKS(acehigh=False)))
	combinations = []
	straight_ranks = []
	for ranks in [sorted_ranks, sorted_ranks_acelow]: 
		for idx,i in enumerate(range(len(ranks)-4)): combinations.append(''.join(ranks[idx:(5+idx)]))
	for c in combinations:
		if (c in ''.join(reversed(RANKS())) or c in ''.join(reversed(RANKS(acehigh=False)))): straight_ranks.append(c)
	return straight_ranks
def GetFlushSuit(cards):
	suits_counts = Counter([card.suit for card in cards])
	return next(iter([suit for (suit,count) in suits_counts.items() if count >= 5]), None)
def GetFlushRanks(cards):
	suits = SUITS()
	flush_cards = []
	combinations = []
	for suit in suits: flush_cards.append([card for card in cards if card.suit == suit and len([card.rank for card in cards if card.suit == suit])>=5])	
	for cards in list(filter(None, flush_cards)):
			for ranks in SortUniqueRanks(cards), SortUniqueRanks(cards, rankdict=ranks_to_rankdict(RANKS(acehigh=False))):
				for idx,i in enumerate(range(len(ranks)-4)): combinations.append(''.join(ranks[idx:(5+idx)]))
	return combinations
def HighCard(cards):
	# Return 5 highest cards
	return SortCardsByRank(cards)[:5]
def Pair(cards):
	return OneRankHand(cards, 2)
def TwoPair(cards):
	# Kickers are the best cards left between the hand and the total 5
	kickers = 1
	pairs = []
	for rank in SortUniqueRanks(cards):
		if sum(card.rank == rank for card in cards) == 2: pairs.append([card for card in cards if card.rank == rank])
	if len(pairs) >=2:
		for card in [card for pair in pairs[:2] for card in pair]: cards.remove(card)
		kicker = SortCardsByRank(cards)[0]
		return [card for pair in pairs[:2] for card in pair] + [kicker]
	return []
def Set(cards):
	return OneRankHand(cards, 3)
def Straight(cards):
	straight_ranks = GetStraightRanks(cards)
	if len(cards) < 5 or len(straight_ranks) == 0: return []
	cards = SortCardsByRank(cards)
	# We want reverse order for a wheel
	if straight_ranks[0] == '5432A': cards = SortCardsByRank(cards, rankdict=ranks_to_rankdict(RANKS(acehigh=False)))
	highest_straight = []
	populate_highest_straight = [ highest_straight.append(card) for card in cards if card.rank in straight_ranks[0] and card.rank not in [card.rank for card in highest_straight] ]
	return highest_straight
def Flush(cards):
	flush_ranks = GetFlushRanks(cards)
	if len(cards) < 5 or len(flush_ranks) == 0: return []
	cards = SortCardsByRank(cards)
	return [ card for card in cards if card.rank in flush_ranks[0] and card.suit == GetFlushSuit(cards) ]
def FullHouse(cards):
	set_ranks = GetRankHandRanks(cards, 3)
	pair_ranks = GetRankHandRanks(cards, 2)
	if len(cards) < 5 or len(set_ranks) == 0 or len(pair_ranks) == 0: return []
	return [ card for card in cards if card.rank in set_ranks[0] ] + [ card for card in cards if card.rank in pair_ranks[0] ]
	# we want to order the full house with set first..
def Quads(cards):
	return OneRankHand(cards, 4)
def StraightFlush(cards):
	straight_ranks = GetStraightRanks(cards)
	flush_ranks = GetFlushRanks(cards)
	if len(cards) < 5 or len(flush_ranks) == 0 or len(straight_ranks) == 0: return []
	straightflush_ranks = [ranks for ranks in flush_ranks if ranks in straight_ranks]
	cards = SortCardsByRank(cards)
	if straightflush_ranks[0] == '5432A': cards = SortCardsByRank(cards, rankdict=ranks_to_rankdict(RANKS(acehigh=False)))
	return [ card for card in cards if card.rank in straightflush_ranks[0] and card.suit == GetFlushSuit(cards) ]
def RoyalFlush(cards):
	straightflush = StraightFlush(cards)
	if len(cards) < 5 or len(straightflush) == 0: return []
	if straightflush[0].rank == "A":
		return straightflush
	return []
def HandRank(cards):
	for hand in reversed(HANDS()):
		hand_cards = globals()[hand](cards)
		if any(hand_cards):
			# It's interesting thinking on how to define the strenght of the hole cards..
			# It's the rank strength but also if suited and the straight possibilities, etc..
			# Obv could google the math but can do this, the sweet spot for straight should be JT or T9
			# Anyway, for now let's rate it using the rank alone. MAX is 24 on 2 cards, so we divide by 24.1 to get 0.99 as we want the rank strength to be the decimal part.
			# And on 5 cards, max is AAAAK which is 59. So we divide by 59.1
			rank_divisor = 12657 if len(hand_cards) == 2 else 17782186352
			weighted_rank_indexes = []
			for idx, card in reverse_enumerate(hand_cards): weighted_rank_indexes.append((RANKS().index(card.rank)+100)**(idx+1))
			strength = HANDS().index(hand) + sum(weighted_rank_indexes)/rank_divisor
			return {'hand': hand, 'cards': hand_cards, 'strength': strength}