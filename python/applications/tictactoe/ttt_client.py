import sys
import time, random
import spacetime
from spacetime import Application
from datamodel import Player, Mark

def my_print(*args):
	print(*args)
	sys.stdout.flush()

def player(dataframe):
    my_player = Player("Team-{0}". format(random.randint(0,500)))
    dataframe.add_one(Player, my_player)
    my_print("Player name: %s" % my_player.player_name)

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
        #marks = dataframe.read_all(Mark)
        #if len(marks) > 0 and marks[0].player_id == my_player.player_id and marks[0].rejected:
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

    if my_player.winner:
        my_print("I WON!!!!!!!!")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    player_client = Application(player, dataframe=("127.0.0.1", port), Types=[Player, Mark], version_by=spacetime.utils.enums.VersionBy.FULLSTATE)
    player_client.start()

