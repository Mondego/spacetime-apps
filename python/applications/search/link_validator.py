import sys, os

sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "../..")))

from spacetime.client.frame import frame
import logging
from datamodel.search.datamodel import NewLink, BadUrlPattern, DownloadLinkGroup, Link, Release
from spacetime.client.IApplication import IApplication
from spacetime.client.declarations import GetterSetter, Deleter, Getter
try:
    # For python 2
    from urlparse import urlparse, parse_qs
except ImportError:
    # For python 3
    from urllib.parse import urlparse, parse_qs


logger = logging.getLogger(__name__)
LOG_HEADER = "[LINKVALIDATOR]"


@Deleter(NewLink, DownloadLinkGroup)
@GetterSetter(NewLink, BadUrlPattern, DownloadLinkGroup)
@Getter(Link, Release)
class LinkValidator(IApplication):

    def __init__(self, frame):
        self.frame = frame
        self.first = True

    def initialize(self):
        pass

    def update(self):
        download_groups = self.frame.get(DownloadLinkGroup)
        new_patterns = self.frame.get_new(BadUrlPattern)
        if len(new_patterns) != 0:
            for dg in download_groups:
                bad_ls = list()
                for l in dg.link_group:
                    for p in new_patterns:
                        if l.url.startswith(p.pattern):
                            bad_ls.append(l)
                            break
                for b in bad_ls:
                    dg.link_group.remove(b)
                    logger.log(logging.INFO, "removing %s" % b.url)
                    print "removing urls"
                if len(dg.link_group) == 0:
                    logger.log(logging.INFO, "Deleting a whole group.")
                    print "deleting groups"
                    self.frame.delete(DownloadLinkGroup, dg)
                elif len(bad_ls) > 0:
                    logger.log(logging.INFO, "Partially deleting links from a group.")
                    print "deleting some few urls only."
                    # reset the list because pcc can only track changes to list on reassignment.
                    dg.link_group = list(dg.link_group)

        if len(self.frame.get(Release)) == 0:
            #print "Blocked"
            return

        #print "Not blocked"
        new_links = self.frame.get_new(NewLink) if not self.first else self.frame.get(NewLink)
        if self.first:
            self.first = False
        for l in new_links:
            if self.is_valid(l):
                l.valid = True
            else:
                self.frame.delete(NewLink, l)

    def shutdown(self):
        pass

    def is_valid(self, l):
        patterns = self.frame.get(BadUrlPattern)
        for pattern in patterns:
            if l.url.startswith(pattern.pattern):
                logger.log(logging.INFO, "Not allowing link %s from entering frontier" % l.url)
                return False
        return True
        #parsed = urlparse(l.full_url)
        #return parsed.scheme != "" and parsed.hostname != "" and ".ics.uci.edu" in parsed.hostname

class Simulation(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        frame_c = frame(time_step = 1000)
        frame_c.attach_app(LinkValidator(frame_c))

        frame_c.run_async()
        frame.loop()

if __name__== "__main__":
    sim = Simulation()
   


