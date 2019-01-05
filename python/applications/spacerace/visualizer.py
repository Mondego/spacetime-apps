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

class SpaceRaceSprite(pygame.sprite.Sprite):
    def __init__(self, go):
        pygame.sprite.Sprite.__init__(self)  #call Sprite initializer

        self.game_object = go
        # We need x, y as floats because pygame's rect uses ints
        self.x = go.global_x 
        self.y = go.global_y
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = [self.x, self.y]

    def move(self, delta, snap):
        # Do we need to snap to world positions?
        if snap:
#            if abs(self.x - self.asteroid.global_x) > 5:
#                my_print("OOPS, big snap for {0}: local={1:.2f} global={2:.2f}".format(self.asteroid.oid, self.x, self.asteroid.global_x))
            self.x, self.y = [self.game_object.global_x, self.game_object.global_y]
        elif self.x <= World.WORLD_WIDTH and self.x >= 0 and self.y <= World.WORLD_HEIGHT and self.y >= 0:
            self.move_delta(delta)
        self.rect.left, self.rect.top = [self.x, self.y]

class AsteroidSprite(SpaceRaceSprite):
    def __init__(self, go):
        self.image = pygame.image.load("art/asteroid.png")
        SpaceRaceSprite.__init__(self, go)  #call Sprite initializer

    def move_delta(self, delta):
            self.x += (self.game_object.velocity * delta)

class ShipSprite(SpaceRaceSprite):
    def __init__(self, go):
        self.image = pygame.image.load("art/ship.png")
        SpaceRaceSprite.__init__(self, go)  #call Sprite initializer
        my_print("New ship sprite {0}".format(self.game_object.player_id))

    def move_delta(self, delta):
        self.y += (self.game_object.velocity * delta)

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
    WORLD_Y_OFFSET = 100
    def __init__(self, world):
        pygame.init()
        self.world = world
        self.width = World.WORLD_WIDTH
        self.height = World.WORLD_HEIGHT + Visualizer.WORLD_Y_OFFSET
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.info = TextBar(self.screen, (50, World.WORLD_HEIGHT - Visualizer.WORLD_Y_OFFSET))

        self.listeners = []

        self.asteroids = []
        # Create the asteroid sprites
        for a in world.asteroids.values():
            self.asteroids.append(AsteroidSprite(a))

        self.ships = {}

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

        # Are there new ships?
        if len(self.world.ships) > len(self.ships):
            for id, go in self.world.ships.items():
                if id not in self.ships:
                    self.ships[id] = ShipSprite(go)

        # Move all sprites
        for obj in self.asteroids + list(self.ships.values()):
            obj.move(Visualizer.DELTA_TIME, snap)
            self.screen.blit(obj.image, obj.rect) 

        # Let others inject messages
        for l in self.listeners:
            l.update_screen()

        pygame.display.update()
        #self.clock.tick(Visualizer.FPS)

        return True

    def register(self, listener):
        self.listeners.append(listener)


