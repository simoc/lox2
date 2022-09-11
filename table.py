class Table:
	"""Implements a hash table using a python dict"""
	def __init__(self):
		self.__entries = {};

	def freeTable(self):
		self.__entries = {};

	def addAll(self, fromTable):
		for k in fromTable.__entries.keys():
			self.__entries[k] = fromTable[k]

	def get(self, key):
		if key in self.__entries:
			return self.__entries[key]
		return None

	def set(self, key, value):
		if key in self.__entries:
			isNewKey = False
		else:
			isNewKey = True
		self.__entries[key] = value
		return isNewKey

	def delete(self, key):
		if key in self.__entries:
			self.__entries.pop(key)
			return True
		return False
