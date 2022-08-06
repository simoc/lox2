
class ValueArray:
	"""Array of constants that are used by a chunk"""

	def __init__(self):
		self.values = []

	def __getitem__(self, item):
		"""Get constant from array by index"""
		return self.values[item]

	def writeValueArray(self, value):
		"""Add a constant to array"""
		self.values.append(value)

	def clear(self):
		"""Clear all constants"""
		self.values.clear()

	def len(self):
		"""Return number of contants in array"""
		return len(self.values)
