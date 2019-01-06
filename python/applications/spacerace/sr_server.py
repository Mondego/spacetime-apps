import time
import sys, random, math
import spacetime
from rtypes import pcc_set, dimension, primarykey
from spacetime import Application
from datamodel import Player, Ship, Asteroid, World, ShipState

def my_print(*args):
    print(*args)
    sys.stdout.flush()

WAIT_FOR_START = 5

def x_gen():
    x = 100
    while True:
        if x >= World.WORLD_WIDTH:
            x = 100
        yield x
        x += World.SHIP_WIDTH + 20

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

class Game(object):
    PHYSICS_FPS = 20 # per second; for collisions
    DELTA_TIME = float(1)/PHYSICS_FPS
    ASTEROID_GENERATION_TICKS = 1
    SYNC_FPS = PHYSICS_FPS / 2

    def __init__(self, df):
        self.dataframe = df
        self.world = World()
        self.current_players = {}
        self.init_asteroids()

    def init_asteroids(self):
        for n in range(World.ASTEROID_COUNT):
            ast = Asteroid()
            self.dataframe.add_one(Asteroid, ast)

    def wait_for_players(self):
        # Delete the previous players and left over ships
        for p in self.current_players:
            self.dataframe.delete_one(Player, p)
        my_print("Ships left over: %d" % len(self.dataframe.read_all(Ship)))
        self.dataframe.delete_all(Ship)

        no_players = True
        while self.dataframe.sync() and no_players:
            players = self.dataframe.read_all(Player)
            if len(players) < 2:
                time.sleep(1)
                continue
            # take just the first 2
            my_print("%d players joined. Taking the first 2." % len(players))
            self.current_players = [players[0], players[1]]
            for player in self.current_players:
                player.ready = True
            no_players = False
            self.world.reset()
            return True

    def play(self):
        # Players joined, start the game
        game_over = False
        ticks = 0
        x = x_gen()
        while not game_over:
            start_t = time.perf_counter()

            # Are there new players?
            players = self.dataframe.read_all(Player)
            for p in players:
                if p.oid not in self.current_players:
                    my_print("New player {0} {1}".format(p.oid, p.player_id))
                    self.current_players[p.oid] = p
                    p.ready(next(x), self.dataframe)

            # Move all asteroids
            self.move_asteroids()

            # Move all ships
            self.move_ships()

            # Check if there were any collistions
            self.detect_collisions()

            # Sync the shared data every so often
            if ticks % 8 == 0:
                self.dataframe.sync()

            ticks += 1
            elapsed_t = time.perf_counter() - start_t
            #my_print("Sleeping for %f" % (Game.DELTA_TIME - elapsed_t))
            time.sleep(Game.DELTA_TIME - elapsed_t)

    def move_asteroids(self):
        for a in self.dataframe.read_all(Asteroid):
            a.move(Game.DELTA_TIME)
        #my_print("position: %d" % (self.dataframe.read_all(Asteroid)[0].global_x))

    def move_ships(self):
        for p in self.current_players.values():
            if p.ship.move(Game.DELTA_TIME):
                p.ship.trips += 1

    def detect_collisions(self):
        for a in self.dataframe.read_all(Asteroid):
            a_top_left = [a.global_x, a.global_y]
            a_bottom_right = [a.global_x + World.ASTEROID_WIDTH, a.global_y + World.ASTEROID_HEIGHT]
            # Let's enlarge the object relative to its velocity
            if a.velocity < 0:
                a_top_left[0] += Game.DELTA_TIME * a.velocity
            else:
                a_bottom_right[0] += Game.DELTA_TIME * a.velocity

            for s in self.dataframe.read_all(Ship):
                # Before we do anything, was it destoyed already?
                if s.state == ShipState.DESTROYED:
                    continue
                # Before we do more computation, are they too far to even consider?
                if math.hypot(s.global_x - a.global_x, s.global_y - a.global_y) > 200:
                    continue

                # Is the asteroid going away from the ship?
                if ((a.velocity < 0 and a.global_x + World.ASTEROID_WIDTH < s.global_x) or 
                    (a.velocity > 0 and a.global_x > s.global_x + World.SHIP_WIDTH)):
                    continue

                s_top_left = [s.global_x, s.global_y]
                s_bottom_right = [s.global_x + World.SHIP_WIDTH, s.global_y + World.SHIP_HEIGHT]
                # Let's enlarge the object relative to its velocity
                s_top_left[1] += Game.DELTA_TIME * s.velocity

#                my_print("Ship and asteroid close s: {0}-{1} {2}-{3}   a: {4}-{5} {6}-{7}".format(s_top_left[0], s_top_left[1], 
#                                                                                                  s_bottom_right[0], s_bottom_right[1], 
#                                                                                                  a_top_left[0], a_top_left[1], 
#                                                                                                  a_bottom_right[0], a_bottom_right[1]))

                if overlap(a_top_left, a_bottom_right, s_top_left, s_bottom_right):
                    s.collision()

    def stop_game(self, players, winner):
        for pid, player in enumerate(self.current_players):
            player.done = True
        if winner >= 0:
            self.current_players[winner].winner = True


def sr_server(dataframe):
    my_print ("READY FOR NEW GAME")
    game = Game(dataframe)
    while True: #game.wait_for_players():
        game.play()
        my_print ("GAME OVER")
        time.sleep(WAIT_FOR_START)


def main(port):
    server = Application(sr_server, server_port=port, Types=[Player, Ship, Asteroid], version_by=spacetime.utils.enums.VersionBy.FULLSTATE)
    server.start()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    main(port)
