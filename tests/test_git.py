import unittest
import os
import io
import sys
import shutil
from optparse import OptionParser
import logging

import coshsh
from coshsh.generator import Generator
from coshsh.datasource import Datasource
from coshsh.application import Application
from coshsh.configparser import CoshshConfigParser
from coshsh.util import setup_logging
from tests.common_coshsh_test import CommonCoshshTest

sys.dont_write_bytecode = True

class CoshshTest(CommonCoshshTest):
    _configfile = 'etc/coshsh.cfg'
    _objectsdir = "./var/objects/test10"

    def print_header(self):
        print("#" * 80 + "\n" + "#" + " " * 78 + "#")
        print("#" + str.center(self.id(), 78) + "#")
        print("#" + " " * 78 + "#\n" + "#" * 80 + "\n")

    def setUps(self):
        self.config = coshsh.configparser.CoshshConfigParser()
        self.config.read('etc/coshsh.cfg')
        self.generator = coshsh.generator.Generator()
        setup_logging()

    def tearDowns(self):
        shutil.rmtree("./var/objects/test10", True)
        pass

#    def test_recipe_max_deltas_default(self):
#        self.print_header()
#        recipe = {'classes_dir': '/tmp', 'objects_dir': '/tmp', 'templates_dir': '/tmp', 'datasources': 'datasource' }
#        datasource = {'name': 'datasource', 'type': 'simplesample'}
#        self.generator.add_recipe(name='recp', **recipe)
#        self.generator.recipes['recp'].add_datasource(**datasource)
#        self.assertTrue(self.generator.recipes['recp'].max_delta == ())
#
#    def test_recipe_max_deltas_simple(self):
#        self.print_header()
#        recipe = {'classes_dir': '/tmp', 'objects_dir': '/tmp', 'templates_dir': '/tmp', 'datasources': 'datasource', 'max_delta': '101' }
#        datasource = {'name': 'datasource', 'type': 'simplesample'}
#        self.generator.add_recipe(name='recp', **recipe)
#        self.generator.recipes['recp'].add_datasource(**datasource)
#        self.assertTrue(self.generator.recipes['recp'].max_delta == (101, 101))
#
#    def test_recipe_max_deltas_double(self):
#        self.print_header()
#        recipe = {'classes_dir': '/tmp', 'objects_dir': '/tmp', 'templates_dir': '/tmp', 'datasources': 'datasource', 'max_delta': '101:202' }
#        datasource = {'name': 'datasource', 'type': 'simplesample'}
#        self.generator.add_recipe(name='recp', **recipe)
#        self.generator.recipes['recp'].add_datasource(**datasource)
#        self.assertTrue(self.generator.recipes['recp'].max_delta == (101, 202))

    def test_create_recipe_multiple_sources(self):
        self.print_header()
        self.generator.add_recipe(name='test10', **dict(self.config.items('recipe_TEST10')))
        self.config.set("datasource_CSV10.1", "name", "csv1")
        self.config.set("datasource_CSV10.2", "name", "csv2")
        self.config.set("datasource_CSV10.3", "name", "csv3")
        cfg = self.config.items("datasource_CSV10.1")
        self.generator.recipes['test10'].add_datasource(**dict(cfg))
        cfg = self.config.items("datasource_CSV10.2")
        self.generator.recipes['test10'].add_datasource(**dict(cfg))
        cfg = self.config.items("datasource_CSV10.3")
        self.generator.recipes['test10'].add_datasource(**dict(cfg))
        # remove target dir / create empty
        self.generator.recipes['test10'].count_before_objects()
        self.generator.recipes['test10'].cleanup_target_dir()

        self.generator.recipes['test10'].prepare_target_dir()
        # check target

        # read the datasources
        self.generator.recipes['test10'].collect()
        self.generator.recipes['test10'].assemble()

        # for each host, application get the corresponding template files
        # get the template files and cache them in a struct owned by the recipe
        # resolve the templates and attach the result as config_files to host/app
        self.generator.recipes['test10'].render()
        self.assertTrue(hasattr(self.generator.recipes['test10'].objects['hosts']['test_host_0'], 'config_files'))
        self.assertTrue('host.cfg' in self.generator.recipes['test10'].objects['hosts']['test_host_0'].config_files['nagios'])

        # write hosts/apps to the filesystem
        self.generator.recipes['test10'].output()
        self.assertTrue(os.path.exists("var/objects/test10/dynamic/hosts"))
        self.assertTrue(os.path.exists("var/objects/test10/dynamic/hosts/test_host_0"))
        self.assertTrue(os.path.exists("var/objects/test10/dynamic/hosts/test_host_0/os_linux_default.cfg"))
        self.assertTrue(os.path.exists("var/objects/test10/dynamic/hosts/test_host_1/os_windows_default.cfg"))
        with io.open("var/objects/test10/dynamic/hosts/test_host_1/os_windows_default.cfg") as f:
            os_windows_default_cfg = f.read()
        self.assertTrue('os_windows_default_check_' in os_windows_default_cfg)
        self.assertTrue(len(self.generator.recipes['test10'].objects['applications']['test_host_1+os+windows2k8r2'].filesystems) == 5)
        # must be sorted
        self.assertTrue([f.path for f in self.generator.recipes['test10'].objects['applications']['test_host_1+os+windows2k8r2'].filesystems] == ['C', 'D', 'F', 'G', 'Z'])
        # git_init is yes by default
        self.assertTrue(os.path.exists("var/objects/test10/dynamic/.git"))

    def test_create_recipe_multiple_sources_no_git(self):
        self.print_header()
        self.generator.add_recipe(name='test10nogit', **dict(self.config.items('recipe_TEST10nogit')))
        self.config.set("datasource_CSV10.1", "name", "csv1")
        self.config.set("datasource_CSV10.2", "name", "csv2")
        self.config.set("datasource_CSV10.3", "name", "csv3")
        cfg = self.config.items("datasource_CSV10.1")
        self.generator.recipes['test10nogit'].add_datasource(**dict(cfg))
        cfg = self.config.items("datasource_CSV10.2")
        self.generator.recipes['test10nogit'].add_datasource(**dict(cfg))
        cfg = self.config.items("datasource_CSV10.3")
        self.generator.recipes['test10nogit'].add_datasource(**dict(cfg))
        # remove target dir / create empty
        self.generator.run()
        self.assertTrue(os.path.exists("var/objects/test10/dynamic/hosts/test_host_1/os_windows_default.cfg"))
        # git_init is yes by default
        self.assertTrue(not os.path.exists("var/objects/test10/dynamic/.git"))

if __name__ == '__main__':
    unittest.main()


