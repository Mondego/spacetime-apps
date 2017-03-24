import logging
from datamodel.search.datamodel import DownloadLinkGroup, UnProcessedLink
from spacetime.client.IApplication import IApplication
from spacetime.client.declarations import Producer, GetterSetter
from time import time


logger = logging.getLogger(__name__)
LOG_HEADER = "[LOADBALANCER]"


@Producer(DownloadLinkGroup)
@GetterSetter(UnProcessedLink)
class LoadBalancer(IApplication):

    def __init__(self, frame):
        self.frame = frame

    def initialize(self):
        pass

    def update(self):
        links = self.frame.get_new(UnProcessedLink)
        domain_to_link = dict()
        for l in links:
            domain_to_link.setdefault(l.domain, list()).append(l)

        sorted_dl = sorted(domain_to_link.items(), key = lambda x: len(x[1]), reverse = True)
        groups = []
        while len(sorted_dl) > 0:
            mark_for_delete = list()
            grp = list()
            for i in range(len(sorted_dl) if len(sorted_dl) <= 5 else 5):
                domain, dlinks = sorted_dl[i]
                grp.append(dlinks.pop())
                if len(dlinks) == 0:
                    mark_for_delete.append(i)
            groups.append(grp)
            for i in mark_for_delete[::-1]:
                sorted_dl.remove(sorted_dl[i])
        for grp in groups:
            self.frame.add(DownloadLinkGroup(grp))

    def shutdown(self):
        pass

        