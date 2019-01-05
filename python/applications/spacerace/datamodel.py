import sys, random, uuid
from enum import Enum
from rtypes import pcc_set
from rtypes import dimension, primarykey

def my_print(*args):
    print(*args)
    sys.stdout.flush()

class ShipState(Enum):
    DESTROYED = 0
    RUNNING = 1

@pcc_set
class Player(object):
    oid = primarykey(str)
    player_id = dimension(str)
    ready = dimension(bool)
    trips = dimension(int)
    done = dimension(bool)
    winner = dimension(bool)

    def __init__(self, dataframe):
        self.oid = str(uuid.uuid4())
        self.player_id = "Team-{0}". format(random.randint(0,500))
        self.ready = False
        self.trips = 0
        self.done = False
        self.winner = False
        # not shared
        self.ship = Ship()
        self.world = World()
        self.dataframe = dataframe
    
    def act(self):
        # This is pretty brain dead: just keep going,
        # ignore all asteroids
        if self.ship.state == ShipState.RUNNING:
            pass
        elif self.ship.state == ShipState.DESTROYED:
            # Delete the dead ship from the game
            self.dataframe.delete_one(Ship, self.ship)
            # Create a new ship
            self.ship = Ship()
            self.ship.go()
            self.dataframe.add_one(Ship, self.ship)

    def game_over(self):
        if self.winner:
            my_print("I WON!!!!!!!!")

@pcc_set
class Ship(object):
    oid = primarykey(str)
    player_id = dimension(str)
    global_y = dimension(int)
    velocity = dimension(float)
    status = dimension(int)

    def __init__(self):
        self.oid = str(uuid.uuid4())
        self.velocity = 0
        self.global_y = 0
        self.trips = 0
        self.state = ShipState.RUNNING

        self.x = 0

    def go(self):
        self.velocity = 10

    def stop(self):
        self.velocity = 0

@pcc_set
class Asteroid(object):
    oid = primarykey(str)
    global_x = dimension(float)
    global_y = dimension(float)
    velocity = dimension(float)

    def __init__(self):
        self.oid = str(uuid.uuid4())
        self.global_x, self.global_y, self.velocity = Asteroid._random_asteroid_data()
        my_print("New asteroid at {0:.2f}-{1:.2f} vel={2:.2f}".format(self.global_x, self.global_y, self.velocity))

    def move(self, delta):
        self.global_x += (self.velocity * delta)
        #my_print("Asteroid at {0:.2f}-{1:.2f} vel={2:.2f}".format(self.global_x, self.global_y, self.velocity))
        # Did it reach the end?
        if self.global_x >= World.WORLD_WIDTH or self.global_x <= 0:
            self.global_x, self.global_y, self.velocity = Asteroid._random_asteroid_data()

    def _random_asteroid_data():
        x = float(random.randint(0, 1) * World.WORLD_WIDTH)
        y = float(random.randint(0, World.ASTEROID_MIN_Y))
        speed = float(random.randint(World.ASTEROID_MIN_SPEED, World.ASTEROID_MAX_SPEED))
        vel = speed if x == 0 else speed * -1
        return x, y, vel


class World(object):
    """ Represents the world itself. Objects of this type are not
        being shared but they refer to objects that are.
    """
    WORLD_WIDTH = 900 # px
    WORLD_HEIGHT = 900 # px
    SHIP_WIDTH = 30 # px
    SHIP_HEIGHT = 40 # px
    ASTEROID_WIDTH = 7 # px
    ASTEROID_HEIGHT = 3 # px
    ASTEROID_MIN_Y = WORLD_HEIGHT - 42 # px (counting from the top, y goes down)
    ASTEROID_MIN_SPEED = 50 # px/sec
    ASTEROID_MAX_SPEED = 200 # px/sec, i.e. go across the screen in 1 sec
    ASTEROID_COUNT = 10

    def __init__(self):
        self.ships = {}
        self.asteroids = {}

    def reset(self):
        self.ships = []
        self.asteroids = []

    def render(self):
        my_print(" ")
        pass # for now
