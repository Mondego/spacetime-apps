import sys
import time
import spacetime
from spacetime import Application
from datamodel import Player, Asteroid, Ship, World

def my_print(*args):
    print(*args)
    sys.stdout.flush()

SYNC_TIME = 0.1 # secs

def bot_driver(dataframe):
    my_player = Player(dataframe)
    dataframe.add_one(Player, my_player)
    dataframe.sync()
    my_player.init_world()

    trips = 0
    done = False
    while not done:
        start_t = time.perf_counter()

        dataframe.sync()
        survived = my_player.act()

        if not survived:
            # Timeout
            time.sleep(5)
            my_player.reset()
            continue

        if my_player.trips > trips:
            my_print("Successful trips: {0}". format(my_player.trips))
            trips = my_player.trips

        elapsed_t = time.perf_counter() - start_t
        sleep_t = SYNC_TIME - elapsed_t
        if sleep_t > 0:
            time.sleep(sleep_t)
        else:
            my_print("Skipped a beat, elapsed was {0}".format(elapsed_t))

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    vis_client = Application(bot_driver, dataframe=("127.0.0.1", port), Types=[Player, Asteroid, Ship], version_by=spacetime.utils.enums.VersionBy.FULLSTATE)
    vis_client.start()

