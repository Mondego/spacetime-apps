import sys
import time, argparse
import spacetime
from spacetime import Node
from datamodel import Player, Asteroid, Ship, World

def my_print(*args):
    print(*args)
    sys.stdout.flush()

SYNC_TIME = 0.3 # secs

def bot_driver(dataframe, player_class):
    dataframe.pull()
    dataframe.checkout()
    my_player = player_class(dataframe)
    dataframe.add_one(Player, my_player)
    dataframe.commit()
    dataframe.push()
    my_player.init_world()

    trips = 0
    done = False
    while not done:
        start_t = time.perf_counter()

        dataframe.pull()
        dataframe.checkout()
        survived = my_player.act()
        dataframe.commit()
        dataframe.push()

        if not survived:
            # Timeout
            time.sleep(5)
            my_player.reset()
            dataframe.commit()
            dataframe.push()
            continue

        if my_player.ship.trips > trips:
            my_print("Successful trips: {0}". format(my_player.ship.trips))
            trips = my_player.ship.trips

        elapsed_t = time.perf_counter() - start_t
        sleep_t = SYNC_TIME - elapsed_t
        if sleep_t > 0:
            time.sleep(sleep_t)
        else:
            my_print("Skipped a beat, elapsed was {0}".format(elapsed_t))

def get_class( kls ):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='127.0.0.1', help='The hostname of the remote dataframe (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8000, help='The port of the remote dataframe (default: 8000)')
    parser.add_argument('--player', type=str, default='datamodel.Player', help='The class of your player (default: datamodel.Player)')
    args = parser.parse_args()

    my_print("%s %s %s" % (args.host, args.port, args.player))

    player_client = Node(bot_driver, dataframe=(args.host, args.port), Types=[Player, Asteroid, Ship])
    player_client.start(get_class(args.player))

if __name__ == "__main__":
    main()


