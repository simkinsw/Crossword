class Square:

	def __init__(self, row, col, num, val, sol, anum, dnum):
		self.row = row
		self.col = col
		if sol == ".":
			self.color = "black"
			self.value = None
			self.solution = None
			self.number = None
			self.anum = -1
			self.dnum = -1
		else:
			self.color = "white"
			self.value = val
			self.solution = sol
			self.anum = anum
			self.dnum = dnum
			if num == "_":
				self.number = None
			else:
				self.number = num
