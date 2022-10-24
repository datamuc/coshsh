import unittest
import os
import sys
import shutil
from optparse import OptionParser
from configparser import RawConfigParser
import logging

import coshsh
from coshsh.generator import Generator
from coshsh.datasource import Datasource
from coshsh.datarecipient import Datarecipient
from coshsh.application import Application
from coshsh.util import setup_logging
from tests.common_coshsh_test import CommonCoshshTest

sys.dont_write_bytecode = True

class CoshshTest(CommonCoshshTest):
    _configfile = 'etc/coshsh3.cfg'
    _objectsdir = ["./var/objects/test20", "./var/objects/test20se"]

    def print_header(self):
        print("#" * 80 + "\n" + "#" + " " * 78 + "#")
        print("#" + str.center(self.id(), 78) + "#")
        print("#" + " " * 78 + "#\n" + "#" * 80 + "\n")

    def setUps(self):
        shutil.rmtree("./var/objects/test20", True)
        os.makedirs("./var/objects/test20")
        shutil.rmtree("./var/objects/test20se", True)
        os.makedirs("./var/objects/test20se")
        self.config = RawConfigParser()
        self.config.read('etc/coshsh3.cfg')
        self.generator = coshsh.generator.Generator()
        setup_logging()

    def tearDowns(self):
        #shutil.rmtree("./var/objects/test20", True)
        print()

    def test_output(self):
        self.print_header()
        self.generator.add_recipe(name='test20', **dict(self.config.items('recipe_test20')))
        self.config.set("datasource_CSV20.1", "name", "csv20.1")
        cfg = self.config.items("datasource_CSV20.1")
        self.generator.recipes['test20'].add_datasource(**dict(cfg))
        self.config.set("datarecipient_CSV20.1", "name", "csv20.1")
        cfg = self.config.items("datarecipient_CSV20.1")
        self.generator.recipes['test20'].add_datarecipient(**dict(cfg))
        recipe = self.generator.recipes['test20']
        recipe.add_datarecipient(**dict([('type', 'datarecipient_coshsh_default'), ('name', 'datarecipient_coshsh_default'), ('objects_dir', recipe.objects_dir), ('max_delta', recipe.max_delta), ('max_delta_action', recipe.max_delta_action), ('safe_output', recipe.safe_output)]))
        self.generator.recipes['test20'].collect()
        self.generator.recipes['test20'].assemble()
        self.generator.recipes['test20'].render()
        self.generator.recipes['test20'].output()
        self.assertTrue(os.path.exists('var/objects/test20se/dynamic/targets/snmp_switch1.json'))
        self.assertTrue(not os.path.exists('var/objects/test20/dynamic/snmp_switch1.json'))
        self.assertTrue(os.path.exists('var/objects/test20/dynamic/hosts/switch1/os_ios_default.cfg'))


    def test_output_mixed(self):
        self.print_header()
        self.generator.add_recipe(name='test20', **dict(self.config.items('recipe_test21')))
        self.config.set("datasource_CSV20.1", "name", "csv20.1")
        cfg = self.config.items("datasource_CSV20.1")
        self.generator.recipes['test20'].add_datasource(**dict(cfg))
        self.config.set("datarecipient_CSV20.2", "name", "csv20.2")
        cfg = self.config.items("datarecipient_CSV20.2")
        print(self.generator.recipes)
        self.generator.recipes['test20'].add_datarecipient(**dict(cfg))
        recipe = self.generator.recipes['test20']
        recipe.add_datarecipient(**dict([('type', 'datarecipient_coshsh_default'), ('name', 'datarecipient_coshsh_default'), ('objects_dir', recipe.objects_dir), ('max_delta', recipe.max_delta), ('max_delta_action', recipe.max_delta_action), ('safe_output', recipe.safe_output)]))
        self.generator.recipes['test20'].collect()
        self.generator.recipes['test20'].assemble()
        self.generator.recipes['test20'].render()
        self.generator.recipes['test20'].output()
        self.assertTrue(os.path.exists('var/objects/test21/dynamic/hosts/switch1/os_ios_default.cfg'))
        self.assertTrue(os.path.exists('var/objects/test21/dynamic/targets/snmp_switch1.json'))

if __name__ == '__main__':
    unittest.main()


