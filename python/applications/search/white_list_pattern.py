import sys, os, re
import argparse

sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "../..")))

from spacetime.client.frame import frame
import logging
from datamodel.search.datamodel import BadLink, BadUrlPattern, Link
from spacetime.client.IApplication import IApplication
from spacetime.client.declarations import GetterSetter, Producer
try:
    # For python 2
    from urlparse import urlparse, parse_qs
except ImportError:
    # For python 3
    from urllib.parse import urlparse, parse_qs
import cPickle

logger = logging.getLogger(__name__)
LOG_HEADER = "[MANUALBANNER]"

@GetterSetter(BadUrlPattern)
@Deleter(BadUrlPattern)
class WhiteLister(IApplication):
    def __init__(self, frame, pattern):
        self.frame = frame
        self.pattern = pattern

    def initialize(self):
        pass

    def update(self):
        obj = self.frame.get(BadUrlPattern, self.pattern)
        if obj:
            self.frame.delete(BadUrlPattern, obj)
        else:
            print "Did not find pattern in server"
        self.done = True
    
    def shutdown(self):
        print "Done"

                
class Simulation(object):
    '''
    classdocs
    '''
    def __init__(self, address, port, pattern):
        '''
        Constructor
        '''
        frame_c = frame(address = "http://" + address + ":" + port, time_step = 1000)
        frame_c.attach_app(WhiteLister(frame_c, pattern))
        frame_c.run()

if __name__== "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=str, help='Address of the server.')
    parser.add_argument('-p', '--port', type=str,  help='Port of the server.')
    parser.add_argument('-t', '--pattern', type=str, help='Pattern to ban.')
    args = parser.parse_args()
    sim = Simulation(args.address, args.port, args.pattern)
