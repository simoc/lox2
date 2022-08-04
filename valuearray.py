
class ValueArray:
	def __init__(self):
		self.values = []

	def __getitem__(self, item):
		return self.values[item]

	def writeValueArray(self, value):
		self.values.append(value)

	def clear(self):
		self.values.clear()

	def len(self):
		return len(self.values)
