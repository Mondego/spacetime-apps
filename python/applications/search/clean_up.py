import sys, os, re
import argparse

sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "../..")))

from spacetime.client.frame import frame
import logging
from datamodel.search.datamodel import BadLink, BadUrlPattern, Link, DownloadLinkGroup
from spacetime.client.IApplication import IApplication
from spacetime.client.declarations import GetterSetter, Producer, Deleter
try:
    # For python 2
    from urlparse import urlparse, parse_qs
except ImportError:
    # For python 3
    from urllib.parse import urlparse, parse_qs
import cPickle

logger = logging.getLogger(__name__)
LOG_HEADER = "[MANUALBANNER]"

@GetterSetter(DownloadLinkGroup)
@Deleter(DownloadLinkGroup)
class CleanUp(IApplication):
    def __init__(self, frame):
        self.frame = frame

    def initialize(self):
        pass

    def update(self):
        count = 0
        dgs = self.frame.get(DownloadLinkGroup)
        print "Going through ", len(dgs)
        i = 0
        for dg in dgs:
            lc = 0
            for l in dg.link_group:
                lc += 1

            if lc == 0:
                print "Deleting..."
                count += 1
                self.frame.delete(DownloadLinkGroup, dg)
            i += 1
            if i%1000 == 0:
                print i, "/", len(dgs)

        print "Deleted", count
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
        frame_c.attach_app(CleanUp(frame_c))
        frame_c.run()

if __name__== "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=str, help='Address of the server.')
    parser.add_argument('-p', '--port', type=str,  help='Port of the server.')
    args = parser.parse_args()
    sim = Simulation(args.address, args.port)
