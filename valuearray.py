
class ValueArray:
	"""Array of constants that are used by a chunk"""

	def __init__(self):
		self.__values = []

	def __getitem__(self, item):
		"""Get constant from array by index"""
		return self.__values[item]

	def writeValueArray(self, value):
		"""Add a constant to array"""
		self.__values.append(value)

	def clear(self):
		"""Clear all constants"""
		self.__values.clear()

	def len(self):
		"""Return number of contants in array"""
		return len(self.__values)
