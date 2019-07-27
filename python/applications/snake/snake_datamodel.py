'''Snake game's Datamodel.'''
import random
import uuid
import numpy as np
from rtypes import dimension, primarykey
from rtypes import pcc_set


FRAMETIME = 1.0/5

@pcc_set
class Snake():
    '''Defines the snakes which are the player characters in the game.'''
    @property
    def direction_vector(self):
        # pylint: disable=unsubscriptable-object,missing-docstring
        return (np.array(self.snake_position[0]) 
                - np.array(self.snake_position[1]))

    oid = primarykey(str)
    snake_head = dimension(tuple)
    snake_position = dimension(list)
    score = dimension(int)
    start_game = dimension(bool)
    crashed = dimension(bool)
    direction = dimension(int)
    prev_direction = dimension(int)
    assigned_player = dimension(int)

    def __init__(self):
        self.oid = str(uuid.uuid4())
        self.score = 0
        self.start_game = False
        self.crashed = False
        self.direction = 1
        self.prev_direction = 1

    def set_direction(self, direct):
        ''' Sets the new direction for the snake.'''
        self.prev_direction = self.direction
        self.direction = direct
        #print (self.prev_direction, self.direction)

@pcc_set
class Apple():
    ''' Defines the fruit that the snake(s) have to eat.'''
    # pylint: disable=too-few-public-methods
    oid = primarykey(int)
    apple_position = dimension(tuple)

    def __init__(self):
        self.oid = 0
        self.reset_position()

    def reset_position(self):
        '''Resets Apple fruit's position.'''
        self.apple_position = (
            random.randrange(1, World.display_width),
            random.randrange(1, World.display_height))

class World():
    '''Defines the Constants in the World.'''
    # pylint: disable=too-few-public-methods
    display_width = 30
    display_height = 30exit()
    


class Direction():
    '''Enum defining possible key stroke directions.'''
    # pylint: disable=too-few-public-methods
    LEFT = 0
    RIGHT = 1
    DOWN = 2
    UP = 3
