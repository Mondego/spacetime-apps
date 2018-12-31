import sys, random, uuid
from rtypes import pcc_set
from rtypes import dimension, primarykey

def my_print(*args):
	print(*args)
	sys.stdout.flush()

@pcc_set
class Player(object):
	oid = primarykey(str)
	player_id = dimension(int)
	player_name = dimension(str)
	ready = dimension(bool)
	winner = dimension(bool)
	done = dimension(bool)

	def __init__(self, name):
		self.oid = str(uuid.uuid4())
		self.player_name = name
		self.ready = False
		self.done = False
		# Local, non-shared data
		self.board = Board()
		self.marks = []
		self.invalid_marks = []

	def create_mark(self):
		# Do something smarter?
		good = False
		while not good:
			x = random.randint(0,2)
			y = random.randint(0,2)
			if self.board.is_empty(x, y):
				good = True
#			repeated = list(filter(lambda m: m.x == x and m.y == y, self.marks + self.invalid_marks))
#			if len(repeated) == 0:

		mark = Mark(self.player_id, x, y)
		self.board.enforce(mark)
#		self.marks.append(mark)
		return mark

	def invalid_mark(self, mark):
		# The other player has a mark in that spot
		player_id = (self.player_id+1) % 2
		self.board.change_player_id(player_id, mark.x, mark.y)


@pcc_set
class Mark(object):
	oid = primarykey(str)
	player_id = dimension(int)
	x = dimension(int)
	y = dimension(int)
	rejected = dimension(bool)

	def __init__(self, pid, x, y):
		self.oid = str(uuid.uuid4())
		self.player_id = pid
		self.x = x
		self.y = y
		self.rejected = False

class Board(object):
	""" Represents the board itself. Objects of this type are not
		being shared for this blind version of Tic Tac Toe.
	"""
	def __init__(self):
		self.grid = [[" ", " ", " "], 
					 [" ", " ", " "], 
					 [" ", " ", " "]]
		self.mark_count = 0

	def is_empty(self, x, y):
		return self.grid[x][y] == " "

	def enforce(self, mark):
		if self.grid[mark.x][mark.y] == " ":
			self.grid[mark.x][mark.y] = mark.player_id
			self.mark_count += 1
		else:
			my_print("Mark %d-%d sent by %d rejected" % (mark.x, mark.y, mark.player_id))
			mark.rejected = True
		return (self.mark_count == 9)

	def change_player_id(self, id, x, y):
		self.grid[x][y] = str(id)

	def reset(self):
		self.mark_count = 0
		for x in range(3):
			for y in range(3):
				self.grid[x][y] = " "

	def check_game_over(self):
		""" 
			Returns (game_over, winner)
		"""
		# Check rows
		for row in self.grid:
			if row[0] != " " and row[0] == row[1] == row[2]:
				# We have a winner!
				my_print("Winner %s in row %d" % (row[0], self.grid.index(row)))
				return True, int(row[0])
		# Check columns
		for col in range(3):
			if self.grid[0][col] != " " and self.grid[0][col] == self.grid[1][col] == self.grid[2][col]:
				# We have a winner!
				my_print("Winner %s in col %d" % (self.grid[0][col], col))
				return True, int(self.grid[0][col])
		# Check diagonals
		if self.grid[1][1] != " ":
			if self.grid[0][0] == self.grid[1][1] == self.grid[2][2] or self.grid[2][0] == self.grid[1][1] == self.grid[0][2]:
				# We have a winner!
				my_print("Winner %s in diag" % self.grid[1][1])
				return True, int(self.grid[1][1])
		# Is there a tie?
		if self.mark_count == 9:
			return True, -1
		# All other cases
		return False, -1

	def render(self):
		my_print(" ")
		for row in range(3):
			my_print (" | ".join(str(s) for s in self.grid[row]))
			my_print ("--+---+--") if row < 2 else None

