import sys
import time
import spacetime
from spacetime import Application
from datamodel import Player, Mark
from visualizer import Visualizer

def my_print(*args):
	print(*args)
	sys.stdout.flush()

def clip(s):
	return s[0:8]

def visualize(dataframe):
	vis = Visualizer()

	done = False
	while dataframe.sync() and not done:
		time.sleep(0.250)
		marks = dataframe.read_all(Mark)
		players = dataframe.read_all(Player)
		if not vis.update(marks, players):
			break

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    vis_client = Application(visualize, dataframe=("127.0.0.1", port), Types=[Player, Mark], version_by=spacetime.utils.enums.VersionBy.FULLSTATE)
    vis_client.start()

