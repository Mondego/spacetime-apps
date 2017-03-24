import sys, os, re, json
import argparse

sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "../..")))

from spacetime.client.frame import frame
import logging
from datamodel.search.datamodel import BadUrlPattern, Link
from spacetime.client.IApplication import IApplication
from spacetime.client.declarations import Producer

logger = logging.getLogger(__name__)
LOG_HEADER = "[RELOADERBANNER]"
from downloaded_saver import FINAL_FOLDER
@Producer(BadUrlPattern, Link)
class Reloader(IApplication):
    def __init__(self, frame):
        self.frame = frame

    def initialize(self):
        pass

    def update(self):
        print "Adding Bad Patterns."
        dirs = set(os.listdir(FINAL_FOLDER))
        if "bad_patterns.txt" in dirs:
            dirs.remove("bad_patterns.txt")
            for pattern in open(os.path.join(FINAL_FOLDER, "bad_patterns.txt")).readlines():
                fp = pattern.strip()
                if fp:
                    self.frame.add(BadUrlPattern(fp))
        print "Adding Urls"
        count = 0
        for fold in dirs:
            for file in os.listdir(os.path.join(FINAL_FOLDER, fold)):
                try:
                    full_path = os.path.join(FINAL_FOLDER, fold, file)
                    json_link = json.load(open(full_path))
                    l = Link()
                    for dim in Link.__dimensions__:
                        if dim._name in json_link:
                            setattr(l, dim._name, json_link[dim._name])
                
                    
                    self.frame.add(l)
                except Exception:
                    print "Error in:", full_path
                    continue
                count += 1
        print "Added", count, "urls."
        self.done = True
    
    def shutdown(self):
        print "Done"

                
class Simulation(object):
    '''
    classdocs
    '''
    def __init__(self, address, port):
        '''
        Constructor
        '''
        frame_c = frame(address = "http://" + address + ":" + port, time_step = 1000)
        frame_c.attach_app(Reloader(frame_c))
        frame_c.run()

if __name__== "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=str, default="127.0.0.1", help='Address of the server.')
    parser.add_argument('-p', '--port', type=str,  help='Port of the server.')
    args = parser.parse_args()
    sim = Simulation(args.address, args.port)

