import sys, os, re
import argparse

sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "../..")))

from spacetime.client.frame import frame
import logging
from datamodel.search.datamodel import Link
from spacetime.client.IApplication import IApplication
from spacetime.client.declarations import GetterSetter
try:
    # For python 2
    from urlparse import urlparse, parse_qs
except ImportError:
    # For python 3
    from urllib.parse import urlparse, parse_qs
import cPickle

logger = logging.getLogger(__name__)
LOG_HEADER = "[MANUALBANNER]"

@GetterSetter(Link)
class Verify(IApplication):
    def __init__(self, frame, useragent):
        self.frame = frame
        self.useragent = useragent

    def initialize(self):
        pass

    def update(self):
        links = self.frame.get(Link)
        if len(links):
            print "Total links:", len(links)
            print self.useragent, "has touched", len(set([l for l in links if self.is_touched(l, self.useragent)])), "links."
            self.done = True
        else:
            print "Failed to get links"
    
    def shutdown(self):
        print "Done"

    def is_touched(self, l, useragent):
        return useragent in set([l.downloaded_by] + l.bad_url + l.marked_invalid_by)

class Simulation(object):
    '''
    classdocs
    '''
    def __init__(self, address, port, useragentstr):
        '''
        Constructor
        '''
        frame_c = frame(address = "http://" + address + ":" + port, time_step = 1000)
        frame_c.attach_app(Verify(frame_c, useragentstr))
        frame_c.run()

if __name__== "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=str, help='Address of the server.')
    parser.add_argument('-p', '--port', type=str,  help='Port of the server.')
    parser.add_argument('-u', '--useragent', type=str, help='User Agent String to search for.')
    args = parser.parse_args()
    sim = Simulation(args.address, args.port, args.useragent)
