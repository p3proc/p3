#!/usr/bin/env python3
import unittest
from p3.pipeline import *
from p3.settings import default_preproc_settings
from p3 import workflows
import os
import sys
import importlib
import tempfile
from nipype import Workflow
from mock import patch
from .mock_stdout import MockDevice
sys.path.append(os.path.abspath(os.path.dirname(workflows.__file__))) # set default workflows path
current_dir = os.path.dirname(os.path.abspath(os.path.realpath(__file__))) # get the current directory

# get and setup default settings
settings = default_preproc_settings()
settings['output_dir'] = tempfile.TemporaryDirectory().name
settings['tmp_dir'] = os.path.join(settings['output_dir'],'tmp')
settings['bids_dir'] = os.path.join(current_dir,'example_data')
settings['subject'] = ['01','02','03']
settings['debug'] = False

# import default workflows
imported_workflows = {}
for module in settings['workflows']:
    imported_workflows[module] = importlib.import_module('{}.workflow'.format(module))

class test(unittest.TestCase):
    def test_generate_subworkflows(self):
        with patch('sys.stdout',new=MockDevice()) as fake_out:
            # generate subworkflows
            subworkflows = generate_subworkflows(imported_workflows,settings)
            keys = [ # set default keys to test
                'p3_bidsselector',
                'p3_freesurfer',
                'p3_skullstrip',
                'p3_stcdespikemoco',
                'p3_fieldmapcorrection',
                'p3_alignanattoatlas',
                'p3_alignfunctoanat',
                'p3_alignfunctoatlas',
                'p3_create_fs_masks'
            ]
            # assert that the keys generated are equal
            self.assertEqual(
                keys,[key for key in subworkflows]
            )

    def test_generate_connections(self):
        with patch('sys.stdout',new=MockDevice()) as fake_out:
            # generate subworkflows
            subworkflows = generate_subworkflows(imported_workflows,settings)
            # generate connections
            connections = generate_connections(subworkflows,settings)
            links = [(connect[0].fullname,connect[1].fullname) for connect in connections]
            # get connections from settings
            setting_links = [(entry['source'],entry['destination']) for entry in settings['connections']]
            # assert all the links/connections are the same
            for link in links:
                self.assertIn(link,setting_links)

    def test_sideload_nodes(self):
        with patch('sys.stdout',new=MockDevice()) as fake_out:
            # set sideload
            settings['sideload'] = [
                {
                    'workflow': 'p3_bidsselector',
                    'node': 'input',
                    'input': ['subject','test1']
                },
                {
                    'workflow': 'p3_skullstrip',
                    'node': 'input',
                    'input': ['T1','test2']
                },
                {
                    'workflow': 'p3_skullstrip',
                    'node': 'biasfieldcorrect',
                    'input': ['input_image','test3']
                },
            ]
            # generate subworkflows
            subworkflows = generate_subworkflows(imported_workflows,settings)
            # generate connections
            connections = generate_connections(subworkflows,settings)
            # Create Workflow
            p3 = Workflow(name='p3_pipeline')
            # connect nodes
            p3.connect(connections)
            # apply sideloads
            sideload_nodes(p3,connections,settings)
            # check sideloaded fields
            sideload = settings['sideload'][0]
            field = p3.get_node('{}.{}'.format(sideload['workflow'],sideload['node'])).inputs.subject
            self.assertEqual(field,'test1')
            sideload = settings['sideload'][1]
            field = p3.get_node('{}.{}'.format(sideload['workflow'],sideload['node'])).inputs.T1
            self.assertEqual(field,'test2')
            sideload = settings['sideload'][2]
            field = p3.get_node('{}.{}'.format(sideload['workflow'],sideload['node'])).inputs.input_image
            self.assertEqual(field,'test3')

    def test_create_and_run_p3_workflow(self):
        with patch('sys.stdout',new=MockDevice()) as fake_out:
            settings['disable_run'] = True # we can't really test when the pipeline runs, so disable it
            # test pipeline with various settings
            create_and_run_p3_workflow(imported_workflows,settings) # default
            # switch settings
            settings['debug'] = True
            settings['avganats'] = False
            settings['field_map_correction'] = False
            settings['slice_time_correction'] = False
            settings['despiking'] = False
            settings['run_recon_all'] = False
            create_and_run_p3_workflow(imported_workflows,settings) # run with changed settings

if __name__ == '__main__':
    unittest.main()
