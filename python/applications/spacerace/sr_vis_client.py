import sys
import time, argparse
import spacetime
from spacetime import Application
from datamodel import Player, Asteroid, World, Ship
from visualizer import Visualizer

def my_print(*args):
    print(*args)
    sys.stdout.flush()

def clip(s):
    return s[0:8]

def visualize(dataframe):
    dataframe.sync()
    world = World()
    for a in dataframe.read_all(Asteroid):
        world.asteroids[a.oid] = a
    vis = Visualizer(world)

    ticks = 0
    done = False
    while not done:
        start_t = time.perf_counter()
        snap = False
        if ticks % Visualizer.SYNC_TICKS == 0:
            dataframe.sync()
            # Do we have new ships?
            ships = dataframe.read_all(Ship)
            for s in ships:
                if s.oid not in world.ships:
                    world.ships[s.oid] = s
            snap = True
        if not vis.update(snap):
            break
        ticks += 1

        elapsed_t = time.perf_counter() - start_t
        sleep_t = Visualizer.DELTA_TIME - elapsed_t
        if sleep_t > 0:
            time.sleep(sleep_t)
        else:
            my_print("Skipped a beat, elapsed was {0}".format(elapsed_t))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='127.0.0.1', help='The hostname of the remote dataframe (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8000, help='The port of the remote dataframe (default: 8000)')
    args = parser.parse_args()

    my_print("%s %s" % (args.host, args.port))

    player_client = Application(visualize, dataframe=(args.host, args.port), Types=[Asteroid, Ship], version_by=spacetime.utils.enums.VersionBy.FULLSTATE)
    player_client.start()

if __name__ == "__main__":
    main()


