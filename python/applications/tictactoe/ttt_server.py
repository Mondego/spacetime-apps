import time
import sys
import spacetime
from rtypes import pcc_set, dimension, primarykey
from spacetime import Application
from datamodel import Player, Mark

def my_print(*args):
	print(*args)
	sys.stdout.flush()

WAIT_FOR_START = 5

class Game(object):
	def __init__(self, df):
		self.dataframe = df
		self.board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
		self.mark_count = 0
		self.current_players = []

	def wait_for_players(self):
		# Delete the previous players and left over marks
		for p in self.current_players:
			self.dataframe.delete_one(Player, p)
		my_print("Marks left over: %d" % len(self.dataframe.read_all(Mark)))
		self.dataframe.delete_all(Mark)

		no_players = True
		while self.dataframe.sync() and no_players:
			players = self.dataframe.read_all(Player)
			if len(players) < 2:
				time.sleep(1)
				continue
			# take just the first 2
			my_print("%d players joined. Taking the first 2." % len(players))
			self.current_players = [players[0], players[1]]
			for pid, player in enumerate(self.current_players):
				player.player_id = pid
			self.current_players[0].ready = True
			no_players = False
			self.reset_game()
			return True

	def wait_for_marks(self):
		ITERS_TO_QUIT = 10
		n_tries = 0
		while True:
			marks = self.dataframe.read_all(Mark)
			if (len(marks) == 0):
				n_tries = n_tries + 1
				if n_tries < ITERS_TO_QUIT:
					yield None
				else:
					yield marks
			else:
				n_tries = 0
				yield marks

	def stop_game(self, players, winner):
		#players = dataframe.read_all(Player)
		for pid, player in enumerate(self.current_players):
			player.done = True
		if winner >= 0:
			self.current_players[winner].winner = True

	def reset_game(self):
		self.mark_count = 0
		for x in range(3):
			for y in range(3):
				self.board[x][y] = " "

	def enforce(self, mark):
		if self.board[mark.x][mark.y] == " ":
			self.board[mark.x][mark.y] = mark.player_id
			self.mark_count += 1
			# Check if the payer won
		else:
			my_print("Mark %d-%d sent by %d rejected" % (mark.x, mark.y, mark.player_id))
			mark.rejected = True
		return (self.mark_count == 9)

	# Returns (game_over, winner)
	def check_game_over(self):
		# Check rows
		for row in self.board:
			if row[0] != " " and row[0] == row[1] == row[2]:
				# We have a winner!
				my_print("Winner %s in row %d" % (row[0], self.board.index(row)))
				return True, int(row[0])
		# Check columns
		for col in range(3):
			if self.board[0][col] != " " and self.board[0][col] == self.board[1][col] == self.board[2][col]:
				# We have a winner!
				my_print("Winner %s in col %d" % (self.board[0][col], col))
				return True, int(self.board[0][col])
		# Check diagonals
		if self.board[1][1] != " ":
			if self.board[0][0] == self.board[1][1] == self.board[2][2] or self.board[2][0] == self.board[1][1] == self.board[0][2]:
				# We have a winner!
				my_print("Winner %s in diag" % self.board[1][1])
				return True, int(self.board[1][1])
		# Is there a tie?
		if self.mark_count == 9:
			return True, -1
		# All other cases
		return False, -1

	def render(self):
		my_print(" ")
		for row in range(3):
			my_print (" | ".join(str(s) for s in self.board[row]))
			my_print ("--+---+--") if row < 2 else None

def ttt_server(dataframe):
	my_print ("READY FOR NEW GAME")
	game = Game(dataframe)
	while game.wait_for_players():
		# Players joined, start the game
		players = dataframe.read_all(Player)
		game_over = False
		turn = 0
		wait_step = game.wait_for_marks()

		while dataframe.sync() and not game_over:
			marks = next(wait_step)
			if marks == None:
				time.sleep(1)
				continue
			elif len(marks) == 0:
				# Game over, no one placed a mark
				game.stop_game(players, -1)
				break

			# Take only the valid mark(s)
			marks = [m for m in marks if not m.rejected]
			if (len(marks) > 0):
				game.enforce(marks[0])
				game.render()
				game_over, winner = game.check_game_over()

				if game_over:
					game.stop_game(players, winner)
				elif not marks[0].rejected:
					dataframe.delete_one(Mark, marks[0])

				players[turn].ready = False
				turn = (turn + 1) % len(players)
				players[turn].ready = True

			time.sleep(1)

		my_print ("GAME OVER")
		time.sleep(WAIT_FOR_START)


def main(port):
    server = Application(ttt_server, server_port=port, Types=[Player, Mark], version_by=spacetime.utils.enums.VersionBy.FULLSTATE)
    server.start()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    main(port)
