#!/usr/bin/env python
#-*- encoding: utf-8 -*-
#
# Copyright 2010-2012 Gerhard Lausser.
# This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import os
import re
import logging
from host import Host
from datasource import Datasource
from application import Application
from util import compare_attr

logger = logging.getLogger('coshsh')

def __ds_ident__(params={}):
    if compare_attr("type", params, "simplesample"):
        return SimpleSample

class MyHost(Host):
    def __init__(self, params={}):
        superclass = super(MyHost, self)
        superclass.__init__(params)
        self.my_host = True

class SimpleSample(Datasource):
    class_only_the_test_simplesample = True
    def __init__(self, **kwargs):
        self.name = kwargs["name"]
        self.dir = kwargs["dir"]
        self.only_the_test_simplesample = True

    def read(self, filter=None, objects={}):
        logger.info('read items from simplesample')
        self.objects = objects
        hostdata = {
            'host_name': 'test_host_0',
            'address': '127.0.0.9',
            'type': 'test',
            'os': 'Red Hat 6.3',
            'hardware': 'Vmware',
            'virtual': 'vs',
            'notification_period': '7x24',
            'location': 'esxsrv10',
            'department': 'test',
        }
        self.add('hosts', MyHost(hostdata))
        appdata = {
            'name': 'os',
            'type': 'Red Hat',
            'component': '',
            'version': '6.3',
            'patchlevel': '',
            'host_name': 'test_host_0',
            'check_period': '7x24',
        }
        self.add('applications', Application(appdata))
        appdata = {
            'name': 'os',
            'type': 'Windows',
            'component': '',
            'version': '2008',
            'patchlevel': 'R2',
            'host_name': 'test_host_0',
            'check_period': '7x24',
        }
        self.add('applications', Application(appdata))
