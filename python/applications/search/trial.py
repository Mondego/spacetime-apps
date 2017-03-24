import sys, os, re
import argparse

sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "../..")))

from spacetime.client.frame import frame
import logging
from datamodel.search.datamodel import BadLink, BadUrlPattern, Link
from spacetime.client.IApplication import IApplication
from spacetime.client.declarations import GetterSetter, Producer
from trie import Trie
try:
    # For python 2
    from urlparse import urlparse, parse_qs
except ImportError:
    # For python 3
    from urllib.parse import urlparse, parse_qs
import cPickle

logger = logging.getLogger(__name__)
LOG_HEADER = "[MANUALBANNER]"

@GetterSetter(BadLink)
class Trial(IApplication):
    def __init__(self, frame):
        self.frame = frame
        self.trie = Trie()

    def initialize(self):
        pass

    def update(self):
        flag = False
        bls = self.frame.get(BadLink)
        print len(bls)
        for l in bls:
            self.trie.add(l.url, None)

        for t in sorted(Trie.flat_list, key = lambda x: x.count, reverse = True):
            print t.previous, t.count
            flag = True
        if flag:
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
        frame_c.attach_app(Trial(frame_c))
        frame_c.run()

if __name__== "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=str, default="127.0.0.1", help='Address of the server.')
    parser.add_argument('-p', '--port', type=str, default="10000",  help='Port of the server.')
    args = parser.parse_args()
    sim = Simulation(args.address, args.port)
