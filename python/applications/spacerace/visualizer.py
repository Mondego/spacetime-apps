import sys
import time
import operator
from threading import Thread
import spacetime
from spacetime import Application
from datamodel import Player, World, Ship, Asteroid, ShipState
import pygame
from pygame.locals import *
import pygame.freetype

def my_print(*args):
    print(*args)
    sys.stdout.flush()

def clip(s):
    return s[0:5]

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
#            if abs(self.x - self.game_object.global_x) > 15:
#                my_print("OOPS, big snap for {0}: local={1:.2f} global={2:.2f} vel={3:.2f}".format(self.game_object.oid, self.x, self.game_object.global_x, self.game_object.velocity))
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
        #my_print("x={0:.2f} delta={1:.2f} vel={2:.2f}".format(self.x, delta, self.game_object.velocity))

class ShipSprite(SpaceRaceSprite):
    def __init__(self, go):
        self.images = [pygame.image.load("art/ship.png")]
        self.image_idx = 0
        self.image = self.images[self.image_idx]
        self.anim_counter = 0
        for i in range(1, 16):
            self.images.append(pygame.image.load("art/ship-destroyed-{0}.png".format(i)))
        SpaceRaceSprite.__init__(self, go)  #call Sprite initializer
        my_print("New ship sprite {0}".format(self.game_object.player_id))

    def move_delta(self, delta):
        if self.game_object.state != ShipState.DESTROYED:
            self.reset()
            self.y += (self.game_object.velocity * delta)
        else:
            self.next_image()

    def next_image(self):
        if self.anim_counter % 4 == 0:
            self.image_idx = min(self.image_idx + 1, len(self.images) - 1)
            self.image = self.images[self.image_idx]
        self.anim_counter += 1

    def reset(self):
        self.image_idx = 0
        self.image = self.images[0]

class TextBar(object):
    def __init__(self, screen, pos, world):
        self.font = pygame.freetype.SysFont(pygame.freetype.get_default_font(), 10)
        self.screen = screen
        self.pos = pos
        self.world = world
        self.update_ticks = 0
        self.message = ""

    def display(self):
        if self.update_ticks % Visualizer.FPS == 0:
            self.message = " " * 20
            trios = [(s.player_id, s.global_x, s.trips) for s in self.world.ships.values()]
            trios.sort(key=operator.itemgetter(1))
            previous_len = 0
            for name, position, trips in trios:
                nm = clip(name)
                #my_print("Position={0} int(p)={1} previous={2}".format(position, int(position/10), previous_len))
                self.message += " " * (int(position/10) - previous_len)
                self.message += nm
                previous_len += len(nm)
        self.update_ticks += 1
        self.font.render_to(self.screen, self.pos, self.message, (0, 255, 0))

class Visualizer(object):
    FPS = 50
    DELTA_TIME = float(1)/FPS
    SYNC_TICKS = 50
    WORLD_Y_OFFSET = 100
    def __init__(self, world):

        pygame.init()
        self.world = world
        self.width = World.WORLD_WIDTH
        self.height = World.WORLD_HEIGHT + Visualizer.WORLD_Y_OFFSET
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.info = TextBar(self.screen, (0, self.height - Visualizer.WORLD_Y_OFFSET + 10), world)

        self.listeners = []

        self.asteroids = []
        # Create the asteroid sprites
        for a in world.asteroids.values():
            self.asteroids.append(AsteroidSprite(a))

        self.ships = {}

        # Sync thread sets this
        self.snap = False

    def run(self):
        done = False
        while not done:
            start_t = time.perf_counter()

            self.screen.fill((0, 0, 0))
            for event in pygame.event.get():
                # my_print("Event %s %s" % (event.type, type(event.type)))
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    pygame.quit()
                    done = True
                if event.type == MOUSEBUTTONDOWN or event.type == 5:
                    for l in self.listeners:
                        l.mouse_down(event)

            # Are there new ships?
            if len(self.world.ships) > len(self.ships):
                for id, go in self.world.ships.items():
                    if id not in self.ships:
                        self.ships[id] = ShipSprite(go)

            # Move all sprites
            snap = self.snap
            for obj in self.asteroids + list(self.ships.values()):
                obj.move(Visualizer.DELTA_TIME, snap)
                self.screen.blit(obj.image, obj.rect) 
            if self.snap:
                self.snap = False

            # Text bar
            self.info.display()

            # Let others inject messages
            for l in self.listeners:
                l.update_screen()

            pygame.display.update()

            elapsed_t = time.perf_counter() - start_t
            sleep_t = Visualizer.DELTA_TIME - elapsed_t
            if sleep_t > 0:
                time.sleep(sleep_t)
            else:
                my_print("pygame thread skipped a beat, elapsed was {0}".format(elapsed_t))

    def snapit(self):
        self.snap = True

    def register(self, listener):
        self.listeners.append(listener)


