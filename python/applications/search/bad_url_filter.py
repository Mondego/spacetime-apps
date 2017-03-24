import sys, os, re

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
LOG_HEADER = "[LINKVALIDATOR]"
NUMBER_OF_URL_BANNERS = 1
THRESHOLD = 5

@GetterSetter(BadLink)
@Producer(BadUrlPattern)
class BadUrlFilter(IApplication):
    def __init__(self, frame):
        self.frame = frame
        self.trie = Trie()

    def initialize(self):
        self.report(self.detect_new_bad_patterns(self.frame.get(BadLink)))

    def update(self):
        self.report(self.detect_new_bad_patterns(self.frame.get_new(BadLink)))
    
    def shutdown(self):
        pass

    def detect_new_bad_patterns(self, links):
        patterns = set()
        for l in links:
            try:
                print "Bad Link", l.full_url
            except UnicodeDecodeError:
                pass
            except UnicodeEncodeError:
                pass
            url = l.url
            if url == "www.ics.uci.edu" or url == "www.ics.uci.edu/":
                continue
            self.trie.add(l.url, l.bad_url)
        for node in (t 
                     for t in sorted(Trie.flat_list, key = lambda x: len(x.reported_by), reverse = True) 
                     if t.count > THRESHOLD and not re.match(r"^www\.ics\.uci\.edu(/(~?[a-zA-Z0-9_]*/?)?)?$", t.previous)):
            pattern = node.previous
            if ".ics.uci.edu" in pattern:
                patterns.add(pattern)
        return patterns

    def report(self, patterns):
        for p in patterns:
            self.frame.add(BadUrlPattern(p))
                
class Simulation(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        frame_c = frame(address = "http://localhost:10000", time_step = 1000)
        frame_c.attach_app(BadUrlFilter(frame_c))

        frame_c.run_async()
        frame.loop()

if __name__== "__main__":
     sim = Simulation()
#    x = BadUrlFilter(10)
#    y1 = Link()
#    y1.url = "archive.ics.uci.edu/ml/dataset?q=hello"
#    y1.scheme = "http"
#    y1.domain = "archive.ics.uci.edu"
#    y1.bad_url = ["crawler1"]

#    y2 = Link()
#    y2.url = "archive.ics.uci.edu/ml/dataset?q=hello"
#    y2.scheme = "http"
#    y2.domain = "archive.ics.uci.edu"
#    y2.bad_url = ["crawler2"]
#    x.detect_new_bad_patterns([y1, y2])
#    with open("domain_banned_patterns.log", "w") as dbp, open("domain_to_longest_prefix.log", "w") as dtlp, open("domain_to_reported_url.log", "w") as dtru:
#        dbp.write("\n".join((k + ": " + str(v) for k, v in x.domain_banned_patterns.items())))
#        dtlp.write("\n".join((k + ": " + str(v) for k, v in x.domain_to_longest_prefix.items())))
#        dtru.write("\n".join((k + ": " + str(v) for k, v in x.domain_to_reported_url.items())))

#    y3 = Link()
#    y3.url = "archive.ics.uci.edu/ml/dataset?q=qwerty"
#    y3.scheme = "http"
#    y3.domain = "archive.ics.uci.edu"
#    y3.bad_url = ["crawler1"]

#    y4 = Link()
#    y4.url = "archive.ics.uci.edu/ml/dataset?q=qwerty"
#    y4.scheme = "http"
#    y4.domain = "archive.ics.uci.edu"
#    y4.bad_url = ["crawler2"]
#    x.detect_new_bad_patterns([y3, y4])

#    with open("domain_banned_patterns.log", "w") as dbp, open("domain_to_longest_prefix.log", "w") as dtlp, open("domain_to_reported_url.log", "w") as dtru:
#        dbp.write("\n".join((k + ": " + str(v) for k, v in x.domain_banned_patterns.items())))
#        dtlp.write("\n".join((k + ": " + str(v) for k, v in x.domain_to_longest_prefix.items())))
#        dtru.write("\n".join((k + ": " + str(v) for k, v in x.domain_to_reported_url.items())))
    



