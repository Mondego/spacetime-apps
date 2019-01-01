import sys, random, time, traceback
from threading import Thread, Event
from datamodel import Player, Mark
import pygame
from pygame.locals import *
from visualizer import Visualizer, TextBar

def my_print(*args):
	print(*args)
	sys.stdout.flush()

class MouseEvent(Event):
    def __init__(self):
        super(MouseEvent, self).__init__()

    def pos(self, x, y):
        self.x = x
        self.y = y

class Opponent(object):
    def __init__(self):
        self.player_name = "Opponent"
        self.player_id = None
        self.done = False

class HumanPlayer(Player):
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
        super(HumanPlayer, self).__init__()
        self.player_name = "You"
        self.marks = []
        self.user_input = MouseEvent()
        Thread(target=self.display).start()
        self.players = [self, Opponent()]
        self.game_started = False
        self.my_turn = False


    def create_mark(self):
        my_print("I'm human!")
        if not self.game_started:
            self.game_started = True
            self.players[1].player_id = (self.player_id + 1) % 2

        self.my_turn = True
        self.user_input.clear()
        my_print("Waiting for user input...")
        self.user_input.wait()
        self.user_input.clear()
        self.my_turn = False

        mark = Mark(self.player_id, self.user_input.x, self.user_input.y)
        self.marks.append(mark)
        return mark

    def display(self):
        display = Visualizer()
        display.register(self)
        self.wait_text = TextBar(display.screen, (20, 555))

        my_print("Update display")
        while True:
            time.sleep(0.250)
            try:
                if not display.update(self.marks, self.players):
                    my_print("Thread exiting")
                    break
            except Exception:
                traceback.print_exc()

    def update_screen(self):
        if self.my_turn:
            self.wait_text.display("Your turn!")
        else:
            self.wait_text.display("Wait...")

    def mouse_down(self, e):
        pos = e.pos
        x = int(pos[1] / 170)
        y = int(pos[0] / 170)
        self.user_input.pos(x, y)
        self.user_input.set()



