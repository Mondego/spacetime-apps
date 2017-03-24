﻿'''
Created on Apr 19, 2016

@author: Rohan Achar
'''

import logging
from datamodel.carpedestrian.datamodel import Walker, ActiveCar
from spacetime.client.IApplication import IApplication
from spacetime.client.declarations import Getter

import pygame
from pygame.locals import *

logger = logging.getLogger(__name__)
LOG_HEADER = "[GFX]"

def load_image(fullname, colorkey=None):
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

class CarSprite(pygame.sprite.Sprite):
    def __init__(self, car):
        self.car_position = car.Position
        self.car_old_position_x = car.Position.X
        self.car_old_position_y = car.Position.Y
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('applications/simulation/images/car-small.gif',-1)
        self.rect.move_ip((self.car_position.X, self.car_position.Y))

    def update(self):
        oldx, oldy = self.car_old_position_x, self.car_old_position_y
        x, y, z = self.car_position.X, self.car_position.Y, self.car_position.Z
        if x != oldx or y != oldy:
            logger.debug("Moving car sprite from (%d, %d) -> (%d, %d)" % (oldx, oldy, x, y))
            self.rect.move_ip((x - oldx, y - oldy))
            self.car_old_position_x, self.car_old_position_y = x, y

class PedestrianSprites(pygame.sprite.Sprite):
    def __init__(self, ped):
        self.ped_X, self.ped_Y = ped.X, ped.Y
        self.ped_oldX, self.ped_oldY = ped.X, ped.Y
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('applications/simulation/images/man-walking-small.gif',-1)
        self.rect.move_ip((self.ped_X, self.ped_Y))

    def update(self):
        if self.ped_X != self.ped_oldX or self.ped_Y != self.ped_oldY:
            logger.debug("Moving ped sprite from (%d, %d) -> (%d, %d)" % (self.ped_oldX, self.ped_oldY, self.ped_X, self.ped_Y))
            self.rect.move_ip((self.ped_X - self.ped_oldX, self.ped_Y - self.ped_oldY))
            self.ped_oldX, self.ped_oldY = self.ped_X, self.ped_Y

@Getter(ActiveCar, Walker)
class GFXSimulation(IApplication):
    '''
    classdocs
    '''

    frame = None
    ticks = 0
    
    def __init__(self, frame):
        '''
        Constructor
        '''
        self.frame = frame
        pygame.init()
        self.width = 640
        self.height = 480
        """Create the Screen"""
        self.screen = pygame.display.set_mode((self.width
                                              ,self.height))
        self.id_to_carsprite = {}
        self.id_to_pedsprite = {}
        self.initialize_screen()

    def initialize_screen(self):
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((255,255,255))

    def initialize(self):
        logger.debug("%s Initializing", LOG_HEADER)

    def update(self):
        cars = self.frame.get(ActiveCar)
        peds = self.frame.get(Walker)
        for car in cars:
            carsprite = self.id_to_carsprite.setdefault(car.ID, CarSprite(car))
            carsprite.car_position = car.Position
            carsprite.update()

        for ped in peds:
            pedsprite = self.id_to_pedsprite.setdefault(ped.ID, PedestrianSprites(ped))
            pedsprite.ped_X = ped.X
            pedsprite.ped_Y = ped.Y
            pedsprite.update()

        self.screen.blit(self.background, (0, 0))
        all_sprites = self.id_to_carsprite.values() + self.id_to_pedsprite.values()
        groups = pygame.sprite.RenderPlain(tuple(all_sprites))
        groups.draw(self.screen)
        pygame.display.flip()
        events = pygame.event.get(pygame.QUIT)
        if events:
            pygame.display.quit()
            self.done = True

    def shutdown(self):
        print "Quitting!!!"
        pass
