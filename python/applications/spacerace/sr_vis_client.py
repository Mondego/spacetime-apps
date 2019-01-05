import sys
import time
import spacetime
from spacetime import Application
from datamodel import Player, Asteroid, World
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

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    vis_client = Application(visualize, dataframe=("127.0.0.1", port), Types=[Asteroid], version_by=spacetime.utils.enums.VersionBy.FULLSTATE)
    vis_client.start()

