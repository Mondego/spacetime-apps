import sys, random, uuid, codecs
from rtypes import pcc_set
from rtypes import dimension, primarykey
from crypto import encrypt_message, generate_key, get_public_key, serialize_public_key, deserialize_public_key

def my_print(*args):
    print(*args)
    sys.stdout.flush()

@pcc_set
class GameMaster(object):
    public_key_serial = dimension(bytes)

    def __init__(self):
        self.private_key = generate_key()
        self.public_key = get_public_key(self.private_key)
        self.public_key_serial = serialize_public_key(self.public_key)
        my_print("My pub key (serial): {0}".format(self.public_key_serial))

    def load_key(self):
        self.public_key = deserialize_public_key(self.public_key_serial)

@pcc_set
class Player(object):
    player_id = dimension(int)
    player_name = dimension(str)
    ready = dimension(bool)
    winner = dimension(bool)
    done = dimension(bool)

    def __init__(self, gm):
        self.player_name = "Team-{0}". format(random.randint(0,500))
        self.ready = False
        self.done = False
        # Local, non-shared data
        self.board = Board()
        self.game_master = gm
        self.game_master.load_key()
        my_print("Game Master's key: {0}".format(self.game_master.public_key))

    def create_mark(self):
        # Do something smarter?
        good = False
        while not good:
            x = random.randint(0,2)
            y = random.randint(0,2)
            if self.board.is_empty(x, y):
                good = True

        mark = Mark(self.player_id, x, y)
        self.board.enforce(mark)
        return mark

    def invalid_mark(self, mark):
        # The other player has a mark in that spot
        player_id = (self.player_id+1) % 2
        self.board.change_player_id(player_id, mark.x, mark.y)

    def game_over(self):
        if self.winner:
            my_print("I WON!!!!!!!!")


@pcc_set
class Mark(object):
    player_id = dimension(int)
    secret_position = dimension(bytes)
    x = dimension(int)
    y = dimension(int)
    rejected = dimension(bool)

    def __init__(self, pid, x, y):
        self.player_id = pid
        self.x = x
        self.y = y
        self.rejected = False
        my_print("New mark for {0}-{1}".format(x, y))

    def hide(self, crypto_key):
        pos_list = [self.x, self.y]; pos_str = str(pos_list)
        ciphertext_bytes = encrypt_message(pos_str, crypto_key)
        self.secret_position = ciphertext_bytes
        self.x = -1
        self.y = -1


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

