#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# This file belongs to coshsh.
# Copyright Gerhard Lausser.
# This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import sys
import os
import re
import imp
import inspect
import logging
import coshsh
from coshsh.util import compare_attr, substenv
from coshsh.datainterface import CoshshDatainterface

logger = logging.getLogger('coshsh')

class DatasourceNotImplemented(Exception):
    pass

class DatasourceNotReady(Exception):
    # datasource is currently being updated
    pass

class DatasourceNotCurrent(Exception):
    # datasources was not updated lately.
    # it makes no sense to continue.
    pass

class DatasourceNotAvailable(Exception):
    pass

class DatasourceCorrupt(Exception):
    pass


class Datasource(CoshshDatainterface):

    my_type = 'datasource'
    class_file_prefixes = ["datasource"]
    class_file_ident_function = "__ds_ident__"
    class_factory = []

    def __init__(self, **params):
        #print "datasourceinit with", self.__class__
        for key in [k for k in params if k.startswith("recipe_")]:
            setattr(self, key, params[key])
            short = key.replace("recipe_", "")
            if not short in params:
                params[short] = params[key]
        for key in params.keys():
            if isinstance(params[key], str):
                params[key] = re.sub('%.*?%', substenv, params[key])
        if self.__class__ == Datasource:
            #print "generic ds", params
            newcls = self.__class__.get_class(params)
            if newcls:
                #print "i rebless anon datasource to", newcls, params
                self.__class__ = newcls
                self.__init__(**params)
            else:
                logger.critical('datasource for %s is not implemented' % params)
                #print "i raise DatasourceNotImplemented"
                raise DatasourceNotImplemented
        else:
            setattr(self, 'name', params["name"])
            self.objects = {}
            pass
        # i am a generic datasource
        # i find a suitable class
        # i rebless
        # i call __init__

    def open(self, **kwargs):
        pass

    def read(self, **kwargs):
        pass

    def close(self):
        pass

    def add(self, objtype, obj):
        try:
            self.objects[objtype][obj.fingerprint()] = obj
        except Exception:
            self.objects[objtype] = {}
            self.objects[objtype][obj.fingerprint()] = obj
        if objtype == 'applications':
            if self.find('hosts', obj.host_name):
                setattr(obj, 'host', self.get('hosts', obj.host_name))

    def get(self, objtype, fingerprint):
        try:
            return self.objects[objtype][fingerprint]
        except Exception:
            # should be None
            return None
            return 'i do not exist. no. no!'

    def getall(self, objtype):
        try:
            return list(self.objects[objtype].values())
        except Exception:
            return []

    def find(self, objtype, fingerprint):
        return objtype in self.objects and fingerprint in self.objects[objtype]

    @classmethod
    def xinit_class_factory(cls, classpath):
        class_factory = []
        print("DS init_classes")
        sys.dont_write_bytecode = True
        for p in [p for p in reversed(classpath) if os.path.exists(p) and os.path.isdir(p)]:
            print("SEARCH DS in "+p)
            for module, path in [(item, p) for item in os.listdir(p) if item[-3:] == ".py" and item.startswith('datasource_')]:
                try:
                    print("TRY DS in "+path+" "+module)
                    #print "try ds", module, path
                    path = os.path.abspath(path)
                    fp, filename, data = imp.find_module(module.replace('.py', ''), [path])
                    toplevel = imp.load_source(module.replace(".py", ""), filename)
                    for cl in inspect.getmembers(toplevel, inspect.isfunction):
                        if cl[0] ==  "__ds_ident__":
                            class_factory.append([path, module, cl[1]])
                            print("ADD DS "+path+" "+module)
                except Exception as exp:
                    logger.critical("could not load datasource %s from %s: %s" % (module, path, exp))
                finally:
                    if fp:
                        fp.close()
        update_class_factory(class_factory)
        return class_factory


    @classmethod
    def xupdate_class_factory(cls, class_factory):
        cls.class_factory = class_factory


    @classmethod
    def xget_class(cls, params={}):
        #print "get_classhoho", cls, len(cls.class_factory), cls.class_factory
        for path, module, class_func in cls.class_factory:
            try:
                #print "try", path, module, class_func
                newcls = class_func(params)
                if newcls:
                    return newcls
            except Exception as exp:
                dsname = 'INVALID' if 'name' not in params else params['name']
                print('Datasource.get_class exception while trying module "%s" for datasource "%s": %s %s' % \
                      (os.path.join(path, module), dsname, type(exp), exp))
                pass
        logger.debug("found no matching class for this datasource %s" % params)




