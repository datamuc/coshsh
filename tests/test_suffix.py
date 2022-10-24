import unittest
import os
import sys
import shutil
from optparse import OptionParser
from configparser import RawConfigParser
import logging


sys.dont_write_bytecode = True

import coshsh
from coshsh.generator import Generator
from coshsh.datasource import Datasource
from coshsh.datarecipient import Datarecipient
from coshsh.application import Application
from coshsh.util import setup_logging
from tests.common_coshsh_test import CommonCoshshTest

class CoshshTest(CommonCoshshTest):
    _configfile = 'etc/coshsh.cfg'
    _objectsdir = "./var/objects/test11"

    def print_header(self):
        print("#" * 80 + "\n" + "#" + " " * 78 + "#")
        print("#" + str.center(self.id(), 78) + "#")
        print("#" + " " * 78 + "#\n" + "#" * 80 + "\n")

    def setUps(self):
        shutil.rmtree("./var/objects/test11", True)
        os.makedirs("./var/objects/test11")
        self.config = RawConfigParser()
        self.config.read('etc/coshsh.cfg')
        self.generator = coshsh.generator.Generator()
        setup_logging()

    def tearDown(self):
        shutil.rmtree("./var/objects/test11", True)
        print()

    def test_create_recipe_collect(self):
        self.print_header()
        self.generator.add_recipe(name='test11', **dict(self.config.items('recipe_TEST11')))
        self.config.set("datasource_SIMPLESAMPLE", "name", "simplesample")
        cfg = self.config.items("datasource_SIMPLESAMPLE")
        self.generator.recipes['test11'].add_datasource(**dict(cfg))
        #self.config.set("datarecipient_SIMPLESAMPLE", "name", "simplesample")
        #cfg = self.config.items("datarecipient_SIMPLESAMPLE")
        #self.generator.recipes['test11'].add_datarecipient(**dict(cfg))
        self.generator.recipes['test11'].collect()
        self.generator.recipes['test11'].assemble()
        self.generator.recipes['test11'].render()
        self.generator.recipes['test11'].output()
        self.assertTrue(os.path.exists('var/objects/test11/dynamic/hosts/test_host_0/nrpe_os_windows_fs.conf'))
        self.assertTrue(os.path.exists('var/objects/test11/dynamic/hosts/test_host_0/os_windows_fs.cfg'))


if __name__ == '__main__':
    unittest.main()


