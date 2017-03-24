import sys, os, json

sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "../..")))
from hashlib import sha1
from spacetime.client.frame import frame
import logging
from datamodel.search.datamodel import AllLink
from spacetime.client.IApplication import IApplication
from spacetime.client.declarations import Getter
import re, chardet


logger = logging.getLogger(__name__)
LOG_HEADER = "[DOWNLOADEDALLSAVER]"
FINAL_FOLDER = "DOWNLOAD_ALL"

@Getter(AllLink)
class AllLinksSaver(IApplication):
    def __init__(self, frame):
        self.frame = frame

    def initialize(self):
        self.save_links(self.frame.get(AllLink))

    def update(self):
        self.save_links(self.frame.get_new(AllLink) + self.frame.get_mod(AllLink))
    
    def shutdown(self):
        pass

    def save_links(self, links):
        
        for l in links:
            try:
                domain = l.domain
                folder = os.path.join(FINAL_FOLDER, domain)
                filename = os.path.join(folder, sha1(l.url).hexdigest())
                #if os.path.exists(filename):
                #    print "File name exists"
                #    continue
                if not os.path.exists(folder):
                
                    try:
                        os.makedirs(folder)
                    except Exception, e:
                        print "Something went wrong", e.message
                        # Something went wrong trying to create the folder
                        continue
                final_l_dict = {}
                for dim in AllLink.__dimensions__:
                    try:
                        final_l_dict[dim._name] = getattr(l, dim._name)
                    except AttributeError:
                        final_l_dict[dim._name] = None

                #final_l_dict = dict(((dim._name, getattr(l, dim._name)) for dim in DownloadedLink.__dimensions__))

                with open(filename, "w") as wfile:
                    try:
                        output = json.dumps(final_l_dict,
                                            sort_keys = True,
                                            indent = 4,
                                            separators = (",",": "))

                        wfile.write(output)
                    except Exception, e1:
                        print "Encoding error maybe? ", e1.message
                        try:
                            detected_encoding = chardet.detect(final_l_dict["raw_content"])['encoding']
                            final_l_dict["raw_content"] = final_l_dict["raw_content"].encode(detected_encoding)
                            if detected_encoding:
                                wfile.write(json.dumps(final_l_dict,
                                            sort_keys = True,
                                            indent = 4,
                                            separators = (",",": "))
                                )  
                        except Exception, e2:
                            print "Final error ", e2.message
                            # Can't do anything more
                            continue
            except Exception, e1:
                try:
                    with open("saver_log.log", "a") as lf:
                        lf.write(l.url + " " + e1.message)
                    continue
                except Exception, e2:
                    with open("saver_log.log", "a") as lf:
                        lf.write("Unknown error")
                    continue
class Simulation(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        frame_c = frame(address = "http://localhost:9000", time_step = 1000)
        frame_c.attach_app(AllLinksSaver(frame_c))

        frame_c.run_async()
        frame.loop()

if __name__== "__main__":
    sim = Simulation()


