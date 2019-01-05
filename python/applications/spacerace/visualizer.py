import sys
import time
import spacetime
from spacetime import Application
from datamodel import Player, World, Ship, Asteroid
import pygame
from pygame.locals import *
import pygame.freetype

def my_print(*args):
    print(*args)
    sys.stdout.flush()

def clip(s):
    return s[0:8]

class AsteroidSprite(pygame.sprite.Sprite):
    def __init__(self, asteroid):
        pygame.sprite.Sprite.__init__(self)  #call Sprite initializer
        self.image = pygame.image.load("art/asteroid.png")

        self.asteroid = asteroid
        # We need x, y as floats because pygame's rect uses ints
        self.x = asteroid.global_x 
        self.y = asteroid.global_y 
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = [self.x, self.y]

    def move(self, delta, snap):
        # Do we need to snap to world positions?
        if snap:
#            if abs(self.x - self.asteroid.global_x) > 5:
#                my_print("OOPS, big snap for {0}: local={1:.2f} global={2:.2f}".format(self.asteroid.oid, self.x, self.asteroid.global_x))
            self.x, self.y = [self.asteroid.global_x, self.asteroid.global_y]
        elif self.x <= World.WORLD_WIDTH or self.x >= 0:
            self.x += (self.asteroid.velocity * delta)
        self.rect.left, self.rect.top = [self.x, self.y]

class TextBar(object):
    def __init__(self, screen, pos):
        self.font = pygame.freetype.SysFont(pygame.freetype.get_default_font(), 30)
        self.screen = screen
        self.pos = pos

    def display(self, message):
        self.font.render_to(self.screen, self.pos, message, (255, 255, 255))

class Visualizer(object):
    FPS = 50
    DELTA_TIME = float(1)/FPS
    SYNC_TICKS = 40
    def __init__(self, world):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.width = World.WORLD_WIDTH
        self.height = World.WORLD_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.info = TextBar(self.screen, (50, World.WORLD_WIDTH - 50))

        self.listeners = []

        self.asteroids = []
        # Create the asteroid sprites
        for a in world.asteroids.values():
            self.asteroids.append(AsteroidSprite(a))

    def update(self, snap):
        self.screen.fill((0, 0, 0))
        for event in pygame.event.get():
            # my_print("Event %s %s" % (event.type, type(event.type)))
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                return False
            if event.type == MOUSEBUTTONDOWN or event.type == 5:
                for l in self.listeners:
                    l.mouse_down(event)

        # Move the asteroid sprites
        for a in self.asteroids:
            a.move(Visualizer.DELTA_TIME, snap)
            self.screen.blit(a.image, a.rect) 

        # Let others inject messages
        for l in self.listeners:
            l.update_screen()

        pygame.display.update()
        #self.clock.tick(Visualizer.FPS)

        return True

    def register(self, listener):
        self.listeners.append(listener)


