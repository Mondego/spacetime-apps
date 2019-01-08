import sys, random, uuid, math
from enum import Enum
from rtypes import pcc_set, merge
from rtypes import dimension, primarykey

def my_print(*args):
    print(*args)
    sys.stdout.flush()

class ShipState:
    DESTROYED = 0
    RUNNING = 1
    STOPPED = 2

@pcc_set
class Player(object):
    oid = primarykey(int)
    player_id = dimension(str)
    ready = dimension(bool)
    done = dimension(bool)
    winner = dimension(bool)

    def __init__(self, dataframe):
        self.oid = random.randint(0, sys.maxsize)
        self.player_id = "T-{0}". format(random.randint(0,500))
        self.ready = False
        self.done = False
        self.winner = False
        # The reference is not shared, but the ship itself is
        self.ship = Ship(self.player_id, 0)
        dataframe.add_one(Ship, self.ship)

        self.world = World()
        self.dataframe = dataframe
    
    def init_world(self):
        for a in self.dataframe.read_all(Asteroid):
            self.world.asteroids[a.oid] = a
        my_print("World has {0} asteroids".format(len(self.world.asteroids)))

    def ready(self, x, df):
        self.ready = True
        self.dataframe = df
        # Find the player's ship
        for s in self.dataframe.read_all(Ship):
            if s.player_id in self.player_id:
                self.ship = s
                self.ship.global_x = float(x)

        my_print("Player {0} ready at {1:.2f} with ship {0}".format(self.player_id, self.ship.global_x, self.ship.oid))

    def act(self):
        #my_print("Ship state is {0}".format(self.ship.state))
        # This is pretty brain dead: just keep going,
        # ignore all asteroids. Let the server do the movement
        # according to the constant velocity set here in "go".
        if self.ship.state == ShipState.STOPPED:
            self.ship.go()
        elif self.ship.state == ShipState.DESTROYED:
            my_print("My ship was destroyed!")
            return False
        return True

    def reset(self):
        self.ship.reset()
        self.ship.go()

    def game_over(self):
        if self.winner:
            my_print("I WON!!!!!!!!")

@pcc_set
class Ship(object):
    oid = primarykey(int)
    player_id = dimension(str)
    global_x = dimension(float)
    global_y = dimension(float)
    velocity = dimension(float)
    state = dimension(int)
    trips = dimension(int)

    def __init__(self, pid, x):
        self.oid = random.randint(0, sys.maxsize)
        self.player_id = pid
        self.velocity = 0.0
        self.global_x = float(x)
        self.global_y = float(World.WORLD_HEIGHT)
        self.trips = 0
        self.state = ShipState.STOPPED
        my_print("New ship at {0:.2f}-{1:.2f} vel={2:.2f}".format(self.global_x, self.global_y, self.velocity))

    def go(self):
        self.velocity = -100.0
        self.state = ShipState.RUNNING

    def stop(self):
        self.velocity = 0.0
        self.state = ShipState.STOPPED

    def reset(self):
        self.stop()
        self.global_y = World.WORLD_HEIGHT

    def move(self, delta):
        """ Returns True upon reaching the finish line, False otherwise
        """
        if self.state == ShipState.RUNNING:
            self.global_y += (self.velocity * delta)

            #my_print("Ship at {0:.2f}-{1:.2f} vel={2:.2f}".format(self.global_x, self.global_y, self.velocity))
        # Did we reach the end?
        if self.global_y <= 0:
            # We got to the finish line!
            my_print("Ship {0} got to the finish line".format(self.oid))
            self.reset()
            return True
        return False

    def collision(self):
        self.state = ShipState.DESTROYED
        self.velocity = 0.0
        my_print("Ship {0} was destroyed".format(self.player_id))

@pcc_set
class Asteroid(object):
    oid = primarykey(int)
    global_x = dimension(float)
    global_y = dimension(float)
    velocity = dimension(float)

    def __init__(self):
        self.oid = random.randint(0, sys.maxsize)
        self.global_x, self.global_y, self.velocity = Asteroid._random_asteroid_data()
        my_print("New asteroid at {0:.2f}-{1:.2f} vel={2:.2f}".format(self.global_x, self.global_y, self.velocity))

    def move(self, delta):
        self.global_x += (self.velocity * delta)
        #my_print("Asteroid at {0:.2f}-{1:.2f} vel={2:.2f} delta={3:.2f}".format(self.global_x, self.global_y, self.velocity, delta))
        # Did it reach the end?
        if self.global_x >= World.WORLD_WIDTH or self.global_x <= 0:
            self.global_x, self.global_y, self.velocity = Asteroid._random_asteroid_data()

    def _random_asteroid_data():
        x = float(random.randint(0, 1) * World.WORLD_WIDTH)
        y = float(random.randint(0, World.ASTEROID_MIN_Y))
        speed = float(random.randint(World.ASTEROID_MIN_SPEED, World.ASTEROID_MAX_SPEED))
        vel = speed if x == 0 else speed * -1
        return x, y, vel
    
    @merge
    def merge_func(original, yours, theirs):
        my_print("Conflict! orig={0:.2f}-{1:.2f} yours={0:.2f}-{1:.2f} theirs={0:.2f}-{1:.2f}".format(original.global_x, original.global_y, yours.global_x, yours.global_y, theirs.global_x, theirs.global_y))
        return theirs

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
    ASTEROID_COUNT = 20

    def __init__(self):
        self.ships = {}
        self.asteroids = {}

    def reset(self):
        self.ships = {}
        self.asteroids = {}

    def render(self):
        my_print(" ")
        pass # for now

def check_collision(a, s, delta_t):
    """ Check collision between a given asteroid a and a given ship s
    """
    # Before we do more computation, are they too far to even consider?
    if math.hypot(s.global_x - a.global_x, s.global_y - a.global_y) > 200:
        return False

    # Is the asteroid going away from the ship?
    if ((a.velocity < 0 and a.global_x + World.ASTEROID_WIDTH < s.global_x) or 
        (a.velocity > 0 and a.global_x > s.global_x + World.SHIP_WIDTH)):
        return False

    s_top_left = [s.global_x, s.global_y]
    s_bottom_right = [s.global_x + World.SHIP_WIDTH, s.global_y + World.SHIP_HEIGHT]
    # Let's enlarge the object relative to its velocity
    s_top_left[1] += delta_t * s.velocity

    a_top_left = [a.global_x, a.global_y]
    a_bottom_right = [a.global_x + World.ASTEROID_WIDTH, a.global_y + World.ASTEROID_HEIGHT]
    # Let's enlarge the object relative to its velocity
    if a.velocity < 0:
        a_top_left[0] += delta_t * a.velocity
    else:
        a_bottom_right[0] += delta_t * a.velocity
#                my_print("Ship and asteroid close s: {0}-{1} {2}-{3}   a: {4}-{5} {6}-{7}".format(s_top_left[0], s_top_left[1], 
#                                                                                                  s_bottom_right[0], s_bottom_right[1], 
#                                                                                                  a_top_left[0], a_top_left[1], 
#                                                                                                  a_bottom_right[0], a_bottom_right[1]))
    if overlap(a_top_left, a_bottom_right, s_top_left, s_bottom_right):
        s.collision()
        return True

    return False

def overlap(topleft1, bottomright1, topleft2, bottomright2):
    """ Returns True if the two rectangles overlap, False otherwise
    """
    # If one rectangle is on the left of the other
    if topleft1[0] > bottomright2[0] or topleft2[0] > bottomright1[0]:
        return False
    # If one rectangle is above the other (remember Y runs down)
    if topleft1[1] > bottomright2[1] or topleft2[1] > bottomright1[1]:
        return False
    return True

