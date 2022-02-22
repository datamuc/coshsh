import unittest
import os
import io
import sys
import shutil
from optparse import OptionParser
import logging


sys.dont_write_bytecode = True

import coshsh
from coshsh.generator import Generator
from coshsh.datasource import Datasource
from coshsh.application import Application
from coshsh.configparser import CoshshConfigParser
from coshsh.util import setup_logging

class CoshshTest(unittest.TestCase):
    def print_header(self):
        print("#" * 80 + "\n" + "#" + " " * 78 + "#")
        print("#" + str.center(self.id(), 78) + "#")
        print("#" + " " * 78 + "#\n" + "#" * 80 + "\n")

    def setUp(self):
        self.config = coshsh.configparser.CoshshConfigParser()
        self.config.read('etc/coshsh.cfg')
        self.generator = coshsh.generator.Generator()
        setup_logging()

    def tearDown(self):
        shutil.rmtree("./var/objects/test10", True)
        pass

    def test_recipe_max_deltas_default(self):
        self.print_header()
        recipe = {'classes_dir': '/tmp', 'objects_dir': '/tmp', 'templates_dir': '/tmp', 'datasources': 'datasource' }
        datasource = {'name': 'datasource', 'type': 'simplesample'}
        self.generator.add_recipe(name='recp', **recipe)
        self.generator.recipes['recp'].add_datasource(**datasource)
        self.assertTrue(self.generator.recipes['recp'].max_delta == ())

    def test_recipe_max_deltas_simple(self):
        self.print_header()
        recipe = {'classes_dir': '/tmp', 'objects_dir': '/tmp', 'templates_dir': '/tmp', 'datasources': 'datasource', 'max_delta': '101' }
        datasource = {'name': 'datasource', 'type': 'simplesample'}
        self.generator.add_recipe(name='recp', **recipe)
        self.generator.recipes['recp'].add_datasource(**datasource)
        self.assertTrue(self.generator.recipes['recp'].max_delta == (101, 101))

    def test_recipe_max_deltas_double(self):
        self.print_header()
        recipe = {'classes_dir': '/tmp', 'objects_dir': '/tmp', 'templates_dir': '/tmp', 'datasources': 'datasource', 'max_delta': '101:202' }
        datasource = {'name': 'datasource', 'type': 'simplesample'}
        self.generator.add_recipe(name='recp', **recipe)
        self.generator.recipes['recp'].add_datasource(**datasource)
        self.assertTrue(self.generator.recipes['recp'].max_delta == (101, 202))

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

        # three mysql objects and three app_db_mysql... files. (in a later test
        # these will not exist because of render exceptions)
        self.assertTrue(len([app for app in self.generator.recipes['test10'].objects['applications'].values() if "mysql" in app.__class__.__name__.lower()]) == 3)
        mysql_files = []
        for mysql in [app for app in self.generator.recipes['test10'].objects['applications'].values() if "mysql" in app.__class__.__name__.lower()]:
            mysql_files.extend([mysql.host_name+"/"+cfg for cfg in mysql.config_files["nagios"].keys()])
        self.assertTrue(len(mysql_files) == 3)
        self.assertTrue(os.path.exists("var/objects/test10/dynamic/hosts/test_host_0/app_db_mysql_intranet_default.cfg"))
        for cfg in mysql_files:
            self.assertTrue(os.path.exists("var/objects/test10/dynamic/hosts/"+cfg))
        self.assertTrue(self.generator.recipes['test10'].render_errors == 0)

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

    def test_create_recipe_set_env(self):
        self.print_header()
        os.environ['OMD_SITE'] = 'sitexy'
        os.environ['COSHSHDIR'] = '/opt/coshsh'
        os.environ['ZISSSSSSCHDIR'] = '/opt/zisch'
        self.generator.add_recipe(name='test7inv', **dict(self.config.items('recipe_TEST7INV')))
        self.config.set("datasource_ENVDIRDS", "name", "envdirds")
        cfg = self.config.items("datasource_ENVDIRDS")
        ds = coshsh.datasource.Datasource(**dict(cfg))
        self.assertTrue(os.environ["THERCP"] == "test7inv_xyz")
        self.assertTrue(os.environ["THECDIR"] == "/opt/coshsh/i_am_the_dir")
        self.assertTrue(os.environ["THEZDIR"] == "/opt/zisch/i_am_the_dir")
        self.assertTrue(os.environ["MIBDIRS"] == "/usr/share/snmp/mibs:/omd/sites/sitexy/etc/coshsh/data/mibs")
        # remove target dir / create empty

    def test_create_recipe_template_error(self):
        self.print_header()
        self.generator.add_recipe(name='test10', **dict(self.config.items('recipe_TEST10tplerr')))
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

        # we have three mysql applications
        self.assertTrue(len([app for app in self.generator.recipes['test10'].objects['applications'].values() if "mysql" in app.__class__.__name__.lower()]) == 3)

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

        self.assertTrue(len([app for app in self.generator.recipes['test10'].objects['applications'].values() if "mysql" in app.__class__.__name__.lower()]) == 3)
        mysql_files = []
        for mysql in [app for app in self.generator.recipes['test10'].objects['applications'].values() if "mysql" in app.__class__.__name__.lower()]:
            self.assertTrue("nagios" not in mysql.config_files)
        self.assertFalse(os.path.exists("var/objects/test10/dynamic/hosts/test_host_0/app_db_mysql_intranet_default.cfg"))
        self.assertTrue(self.generator.recipes['test10'].render_errors == 3)

if __name__ == '__main__':
    unittest.main()


