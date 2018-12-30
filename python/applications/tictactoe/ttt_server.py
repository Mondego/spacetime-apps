import time
import sys
from rtypes import pcc_set, dimension, primarykey
from spacetime import Application
from datamodel import Player, Mark

def my_print(*args):
	print(*args)
	sys.stdout.flush()

WAIT_FOR_START = 10.0

def wait_for_players(dataframe):
	players = list()
	start = time.time()
	while (time.time() - start) < WAIT_FOR_START:
		my_print ("\rWaiting for %d " % (int(WAIT_FOR_START - (time.time() - start)),), "Seconds for clients to connect.")
		time.sleep(1)

	dataframe.checkout()
	players = dataframe.read_all(Player)
	if not players:
		my_print ("No players connected, the game cannot continue. Exiting")
		return False
	my_print("Starting game with %d players" % len(players))
	for pid, player in enumerate(players):
		player.player_id = pid
	players[0].ready = True
	dataframe.commit()
	return True

def wait_for_marks(dataframe):
	ITERS_TO_QUIT = 10
	n_tries = 0
	while True:
		marks = dataframe.read_all(Mark)
		if (len(marks) == 0):
			n_tries = n_tries + 1
			if n_tries < ITERS_TO_QUIT:
				yield None
			else:
				yield marks
		else:
			n_tries = 0
			yield marks

def stop_game(players, winner):
	#players = dataframe.read_all(Player)
	for pid, player in enumerate(players):
		player.done = True
	if winner >= 0:
		players[winner].winner = True

def ttt_server(dataframe):
	if wait_for_players(dataframe):
		# Players joined, start the game
		players = dataframe.read_all(Player)
		game_over = False
		turn = 0
		wait_step = wait_for_marks(dataframe)

		while dataframe.sync() and not game_over:
			marks = next(wait_step)
			if marks == None:
				time.sleep(1)
				continue
			elif len(marks) == 0:
				# Game over, no one placed a mark
				stop_game(players, -1)
				break

			# Take only the valid mark(s)
			marks = [m for m in marks if not m.rejected]
			if (len(marks) > 0):
				enforce(marks[0])
				render()
				game_over, winner = check_game_over()

				if game_over:
					stop_game(players, winner)
				elif not marks[0].rejected:
					dataframe.delete_one(Mark, marks[0])

				players[turn].ready = False
				turn = (turn + 1) % len(players)
				players[turn].ready = True

			time.sleep(1)

	my_print ("game ended, waiting 5 secs for clients to disconnect")
	time.sleep(5)

board = [[" ", " ", " "], 
		 [" ", " ", " "], 
		 [" ", " ", " "]]
mark_count = 0

def enforce(mark):
	global mark_count
	if board[mark.x][mark.y] == " ":
		board[mark.x][mark.y] = mark.player_id
		mark_count += 1
		# Check if the payer won
	else:
		my_print("Mark %d-%d sent by %d rejected" % (mark.x, mark.y, mark.player_id))
		mark.rejected = True
	return (mark_count == 9)

# Returns (game_over, winner)
def check_game_over():
	# Check rows
	for row in board:
		if row[0] != " " and row[0] == row[1] == row[2]:
			# We have a winner!
			my_print("Winner %s in row %d" % (row[0], board.index(row)))
			return True, int(row[0])
	# Check columns
	for col in range(3):
		if board[col][0] != " " and board[col][0] == board[col][1] == board[col][2]:
			# We have a winner!
			my_print("Winner %s in col %d" % (board[col][0], col))
			return True, int(board[col][0])
	# Check diagonals
	if board[1][1] != " ":
		if board[0][0] == board[1][1] == board[2][2] or board[2][0] == board[1][1] == board[0][2]:
			# We have a winner!
			my_print("Winner %s in diag" % board[1][1])
			return True, int(board[1][1])
	# Is there a tie?
	if mark_count == 9:
		return True, -1
	# All other cases
	return False, -1

def render():
	my_print(" ")
	for row in range(3):
		my_print (" | ".join(str(s) for s in board[row]))
		my_print ("--+---+--") if row < 2 else None

def main(port):
    server = Application(ttt_server, server_port=port, Types=[Player, Mark])
    server.start()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    main(port)
