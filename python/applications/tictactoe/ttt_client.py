import sys
import time, random, argparse
import spacetime
from spacetime import Application
from datamodel import Player, Mark

def my_print(*args):
	print(*args)
	sys.stdout.flush()


def player(dataframe, player_class):
    my_player = player_class()
    dataframe.add_one(Player, my_player)
    my_print("Player class is %s and player name is: %s" % (my_player.__class__.__name__, my_player.player_name))

    while dataframe.sync() and not my_player.ready:
        time.sleep(1)
        my_print("Not ready yet %d" % len(dataframe.read_all(Mark)))
        continue

    # Now the game starts
    done = False
    mark = None
    while dataframe.sync() and not done:
        # Slow down to human perception
        time.sleep(1)

        # Check for game over
        if my_player.done:
            break

        # Is it our turn?
        if not my_player.ready:
            continue

        my_print("My turn %d!" % my_player.player_id)

        # Was our previous mark rejected by the server?
        if mark != None and mark.rejected:
            my_print("Mark rejected %d, %d" % (mark.x, mark.y))
            my_player.invalid_mark(mark)
            dataframe.delete_one(Mark, mark)

        mark = my_player.create_mark()
        if mark == None:
            my_print("Can't find a spot!")
            done = True
            continue
        my_print("New mark: %d-%d" % (mark.x, mark.y))
        dataframe.add_one(Mark, mark)
        my_player.ready = False

        done = my_player.done
        my_print("Done? %s" % done)

        my_player.board.render()

    my_print("GAME OVER")
    my_player.game_over()

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

    player_client = Application(player, dataframe=(args.host, args.port), Types=[Player, Mark], version_by=spacetime.utils.enums.VersionBy.FULLSTATE)
    player_client.start(get_class(args.player))

if __name__ == "__main__":
    main()

