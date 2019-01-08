import time
import sys, random, math
import spacetime
from rtypes import pcc_set, dimension, primarykey
from spacetime import Application
from datamodel import Player, Ship, Asteroid, World, ShipState, check_collision

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

class Game(object):
    PHYSICS_FPS = 20 # per second; for collisions
    DELTA_TIME = float(1)/PHYSICS_FPS
    ASTEROID_GENERATION_TICKS = 1

    def __init__(self, df):
        self.dataframe = df
        self.world = World()
        self.current_players = {}
        self.init_asteroids()

    def init_asteroids(self):
        for n in range(World.ASTEROID_COUNT):
            ast = Asteroid()
            self.dataframe.add_one(Asteroid, ast)
        self.dataframe.commit()

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

            self.dataframe.checkout()
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

            self.dataframe.commit()

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
        for s in self.dataframe.read_all(Ship):
            # Before we do anything, was it destoyed already?
            if s.state == ShipState.DESTROYED:
                continue
            for a in self.dataframe.read_all(Asteroid):
                if check_collision(a, s, Game.DELTA_TIME):
                    break

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
    server = Application(sr_server, server_port=port, 
                         Types=[Player, Ship, Asteroid], 
                         version_by=spacetime.utils.enums.VersionBy.FULLSTATE)
    server.start()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    main(port)
