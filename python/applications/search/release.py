import sys, os, re
import argparse

sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "../..")))

from spacetime.client.frame import frame
import logging
from datamodel.search.datamodel import BadLink, BadUrlPattern, Link, Release
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
LOG_HEADER = "[Release]"

@Producer(Release)
class Releaser(IApplication):
    def __init__(self, frame):
        self.frame = frame

    def initialize(self):
        self.frame.add(Release())

    def update(self):
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
        frame_c.attach_app(Releaser(frame_c))
        frame_c.run()

if __name__== "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', default ="127.0.0.1", type=str, help='Address of the server.')
    parser.add_argument('-p', '--port', default = "12000", type=str,  help='Port of the server.')
    args = parser.parse_args()
    sim = Simulation(args.address, args.port)

