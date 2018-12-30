import sys
import time
import spacetime
from spacetime import Application
from datamodel import Player, Mark
import pygame
from pygame.locals import *
import pygame.freetype

def my_print(*args):
	print(*args)
	sys.stdout.flush()

class GridSprite(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)  #call Sprite initializer
		self.image = pygame.image.load("images/grid.png")
		self.rect = self.image.get_rect()
		self.rect.left, self.rect.top = [0,0]

class MarkSprite(pygame.sprite.Sprite):
	def __init__(self, mark):
		pygame.sprite.Sprite.__init__(self)  #call Sprite initializer

		if mark.player_id == 0:
			self.image = pygame.image.load("images/zero.png")
		else:
			self.image = pygame.image.load("images/one.png")

		self.player_id = mark.player_id
		x = mark.y * 512/3 + 42
		y = mark.x * 512/3 + 42
		self.is_bad = False
		self.oid = mark.oid
		self.rect = self.image.get_rect()
		self.rect.left, self.rect.top = [x,y]

	def change_to_bad(self):
		x = self.rect.left - 38
		y = self.rect.top - 38
		self.rect.left, self.rect.top = [x,y]
		if self.player_id == 0:
			self.image = pygame.image.load("images/zero-bad.png")
		else:
			self.image = pygame.image.load("images/one-bad.png")
		self.is_bad = True

class InfoBar(object):
	def __init__(self, screen):
		self.font = pygame.freetype.SysFont(pygame.freetype.get_default_font(), 30)
		self.screen = screen

	def display(self, message):
		self.font.render_to(self.screen, (20, 510), message, (20, 20, 20))

class Visualizer(object):
	def __init__(self):
		pygame.init()
		self.clock = pygame.time.Clock()
		self.width = 512
		self.height = 562
		self.screen = pygame.display.set_mode((self.width, self.height))

		self.background = GridSprite()
		self.marks = []
		self.info = InfoBar(self.screen)

	def update(self, marks, players):
		self.clock.tick(60)
		self.screen.fill((255,255,255))
		self.screen.blit(self.background.image, self.background.rect)
		pygame.event.get()

		# Check what happened with players
		if self.manage_players(players):
			del self.marks[:]

		# Check what happened with marks
		self.manage_marks(marks)
		for m in self.marks:
			self.screen.blit(m.image, m.rect) 

		pygame.display.update()

	def manage_players(self, players):
		reset = False
		if len(players) == 0:
			message = "Waiting for players to join..."
			reset = True

		if len(players) == 1:
			message = "One player joined. Waiting..."

		if len(players) == 2:
			# Is the game over?
			if players[0].done and players[1].done:
				# Who's the winner?
				if players[0].winner:
					message = "{0} WINS!".format(players[0].player_name)
				elif players[1].winner:
					message = "{0} WINS!".format(players[1].player_name)
				else:
					message = "IT'S A TIE!"
			else:
				message = "{0}: {1}    {2}: {3}".format(players[0].player_id, players[0].player_name, players[1].player_id, players[1].player_name)

		self.info.display(message)
		return reset

	def manage_marks(self, marks):
		repeated = []
		for m1 in self.marks:
			for m2 in marks:
				if m1.oid == m2.oid:
					repeated.append(m2)
		for m in marks:
			if m not in repeated:
				my_print("New Mark %d %d-%d" % (m.player_id, m.x, m.y))
				self.marks.append(MarkSprite(m))
			else: # did it change state to rejected?
				if m.rejected:
					mark = next((x for x in self.marks if x.oid == m.oid), None)
					if mark != None and not mark.is_bad:
						mark.change_to_bad()

def visualize(dataframe):
	vis = Visualizer()

	done = False
	while dataframe.sync() and not done:
		time.sleep(0.250)
		marks = dataframe.read_all(Mark)
		players = dataframe.read_all(Player)
		vis.update(marks, players)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    vis_client = Application(visualize, dataframe=("127.0.0.1", port), Types=[Player, Mark], version_by=spacetime.utils.enums.VersionBy.FULLSTATE)
    vis_client.start()

