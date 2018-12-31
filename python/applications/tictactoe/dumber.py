import sys, random
from datamodel import Player, Mark

def my_print(*args):
	print(*args)
	sys.stdout.flush()

class DumberPlayer(Player):
    """
    Example of another kind player. In this case, it does something even dumber
    than the superclass Player: it doesn't even have the concept of the board;
    it just uses lists of marks.
    Use it as:
    $ python ttt_client.py --player dumber.DumberPlayer

    To write your own smater player, do something simlilar, but make the
    create_mark method do something smarter!
    """
    def __init__(self):
        super(DumberPlayer, self).__init__()
        self.player_name = "Dumber"
        self.marks = []
        self.invalid_marks = []

    def create_mark(self):
        my_print("I'm dumber, I don't even use a local board!")
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


