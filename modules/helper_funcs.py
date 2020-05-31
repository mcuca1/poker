def reverse_enumerate(L):
	# Only works on things that have a len()
	l = len(L)
	for i, n in enumerate(L):
		yield l-i-1, n

class ValueContainer(object):
	def __init__(self, value):
		self.value = value
