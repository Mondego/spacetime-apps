#!/usr/bin/python
'''
Created on Jan 17, 2016

@author: Rohan Achar
'''

import logging
import logging.handlers
import os
import sys
import argparse

sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "../..")))

from spacetime.client.frame import frame
from applications.search.load_balancer import LoadBalancer
from applications.search.link_validator import LinkValidator
from applications.search.new_link_generator import NewLinkGenerator
from applications.search.downloaded_saver import DownloadedSaver
from applications.search.bad_url_filter import BadUrlFilter
logger = None

class Simulation(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        frame_lb = frame(address = "http://127.0.0.1:12000", time_step = 1000)
        frame_lb.attach_app(LoadBalancer(frame_lb))
        frame_lv = frame(address = "http://127.0.0.1:12000", time_step = 1000)
        frame_lv.attach_app(LinkValidator(frame_lv))
        frame_nlg = frame(address = "http://127.0.0.1:12000", time_step = 1000)
        frame_nlg.attach_app(NewLinkGenerator(frame_nlg))
        frame_ds = frame(address = "http://127.0.0.1:12000", time_step = 1000)
        frame_ds.attach_app(DownloadedSaver(frame_ds))
        frame_buf = frame(address = "http://127.0.0.1:12000", time_step = 1000)
        frame_buf.attach_app(BadUrlFilter(frame_buf))
        
        frame_lb.run_async()
        frame_lv.run_async()
        frame_nlg.run_async()
        frame_ds.run_async()
        frame_buf.run_async()
        frame.loop()

if __name__== "__main__":
    sim = Simulation()
