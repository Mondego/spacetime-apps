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
		self.marks = []
		self.invalid_marks = []

	def create_mark(self):
		# Do something smarter?
		good = False
		while not good:
			x = random.randint(0,2)
			y = random.randint(0,2)
			repeated = list(filter(lambda m: m.x == x and m.y == y, self.marks + self.invalid_marks))
			if len(repeated) == 0:
				good = True

		mark = Mark(self.player_id, x, y)
		self.marks.append(mark)
		return mark

	def invalid_mark(self, mark):
		self.invalid_marks.append(mark)


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