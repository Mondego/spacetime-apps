import logging
from datamodel.search.datamodel import ProducedLink, OneUnProcessedGroup, robot_manager
from spacetime.client.IApplication import IApplication
from spacetime.client.declarations import Producer, GetterSetter, Getter
from lxml import html,etree
import re, os
from time import time
from uuid import uuid4

try:
    # For python 2
    from urlparse import urlparse, parse_qs
except ImportError:
    # For python 3
    from urllib.parse import urlparse, parse_qs
from uuid import uuid4

logger = logging.getLogger(__name__)
LOG_HEADER = "[CRAWLER]"
unique_id = uuid4()
url_count = 0 if not os.path.exists("successful_urls_%s.txt" % unique_id) else (len(open("successful_urls_%s.txt" % unique_id).readlines()) - 1)
if url_count < 0:
    url_count = 0
MAX_LINKS_TO_DOWNLOAD = 20000

@Producer(ProducedLink)
@GetterSetter(OneUnProcessedGroup)
class CrawlerFrame(IApplication):

    def __init__(self, frame, app_name, useragent):
        self.starttime = time()
        self.app_id = app_name
        self.frame = frame
        self.UserAgentString = useragent + str(uuid4())
        if url_count >= MAX_LINKS_TO_DOWNLOAD:
            self.done = True

    def initialize(self):
        self.count = 0
        l = ProducedLink("http://www.ics.uci.edu/", self.UserAgentString)
        print l.full_url
        self.frame.add(l)

    def update(self):
        groups = self.frame.get(OneUnProcessedGroup)
        for g in groups:
            print "Got a Group", len(groups)
            outputLinks, urlResps = process_url_group(g, self.UserAgentString)
            for urlResp in urlResps:
                if urlResp.bad_url and self.UserAgentString not in set(urlResp.dataframe_obj.bad_url):
                    urlResp.dataframe_obj.bad_url += [self.UserAgentString]
            for l in outputLinks:
                if is_valid(l) and robot_manager.Allowed(l, self.UserAgentString):
                    lObj = ProducedLink(l, self.UserAgentString)
                    self.frame.add(lObj)
        if url_count >= MAX_LINKS_TO_DOWNLOAD:
            self.done = True

    def shutdown(self):
        print "downloaded ", url_count, " in ", time() - self.starttime, " seconds."
        pass

def save_count(urls):
    global url_count
    url_count += len(urls)
    with open("successful_urls_%s.txt" % unique_id, "a") as surls:
        surls.write(("\n".join(urls) + "\n").encode("utf-8"))

def process_url_group(group, useragentstr):
    rawDatas, successfull_urls = group.download(useragentstr, is_valid)
    save_count(successfull_urls)
    return extract_next_links(rawDatas), rawDatas
    
def extract_next_links(rawDatas):
    outputLinks = []
    for rawDataObj in rawDatas:
        url, rawData = rawDataObj.url, rawDataObj.content
        if rawDataObj.is_redirected and rawDataObj.final_url != unicode(url + "/"):
            try:
                print "Marking " + url + " as bad.", rawDataObj.final_url
            except Exception:
                print "E: Marking " + rawDataObj.final_url + " as bad.", rawDataObj.final_url
            rawDataObj.bad_url = True
        if not rawData:
            try:
                print ("Error downloading " + url)
            except Exception:
                continue
            continue
        try:
            htmlParse = html.document_fromstring(rawData)
            htmlParse.make_links_absolute(url if not rawDataObj.is_redirected else rawDataObj.final_url)
        except etree.ParserError:
            print("ParserError: Could not extract the links from the url")
            continue
        except etree.XMLSyntaxError:
            print("XMLError: Could not extract the links from the url")
            continue
        except TypeError:
            print "bad url when making absolute"
            rawDataObj.bad_url = True
        olinks = set()
        for element, attribute, link, pos in htmlParse.iterlinks():
            if link != url:
                olinks.add(link)
        rawDataObj.out_links = olinks
        outputLinks.extend(list(olinks))
    return outputLinks

def is_valid(url):
    parsed = urlparse(url)
    if parsed.scheme not in set(["http", "https"]):
        return False
    try:
        return ".ics.uci.edu" in parsed.hostname \
            and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4"\
            + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
            + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
            + "|thmx|mso|arff|rtf|jar|csv"\
            + "|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()) \
            and "calendar.ics.uci.edu" not in parsed.hostname \
            and "archive.ics.uci.edu/ml/dataset?" not in url \
            and "ganglia.ics.uci.edu" not in url

    except TypeError:
        print ("TypeError for ", parsed)
