from collections import defaultdict

class Value(object):
	def __init__(self, value):
		self.value = value


class CustomDefaultDict(defaultdict):
    def __missing__(self, key):
        self[key] = value = Value(0)
        return value

toy = CustomDefaultDict()

toy['Player1'].value += 15

print(toy['Player1'].value)