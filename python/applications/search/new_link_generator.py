import sys, os

sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "../..")))

from spacetime.client.frame import frame
import logging
from datamodel.search.datamodel import Link, ProducedLink
from spacetime.client.IApplication import IApplication
from spacetime.client.declarations import GetterSetter, Deleter, Getter, Producer
try:
    # For python 2
    from urlparse import urlparse, parse_qs
except ImportError:
    # For python 3
    from urllib.parse import urlparse, parse_qs
from time import localtime, strftime

logger = logging.getLogger(__name__)
LOG_HEADER = "[NEWLINKGENERATOR]"


@Deleter(ProducedLink)
@Getter(ProducedLink)
@Producer(Link)
class NewLinkGenerator(IApplication):

    def __init__(self, frame):
        self.frame = frame
        self.first = True
        self.logfile = open("link_producer.log", "a")

    def initialize(self):
        pass

    def update(self):
        produced_links = self.frame.get_new(ProducedLink)
        strtime = strftime("%a, %d %b %Y %H:%M:%S", localtime())
        self.logfile.write("\n".join(["||".join(strtime, l.full_url, l.downloaded_by) for l in produced_links]) + "\n")
        for l in ProducedLink:
            self.frame.add(Link(l))
            self.frame.delete(ProducedLink, l)

    def shutdown(self):
        pass

class Simulation(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        frame_c = frame(time_step = 1000)
        frame_c.attach_app(NewLinkGenerator(frame_c))

        frame_c.run_async()
        frame.loop()

if __name__== "__main__":
    sim = Simulation()
   


