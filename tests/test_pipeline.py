#!/usr/bin/env python3
import unittest
from p3.pipeline import *
from p3.settings import default_preproc_settings
from p3 import workflows
import os
import sys
import importlib
from nipype import Workflow
sys.path.append(os.path.abspath(os.path.dirname(workflows.__file__))) # set default workflows path
current_dir = os.path.dirname(os.path.abspath(os.path.realpath(__file__))) # get the current directory

# get and setup default settings
settings = default_preproc_settings()
settings['tmp_dir'] = './'
settings['output_dir'] = './'
settings['bids_dir'] = os.path.join(current_dir,'example_data')
settings['subject'] = ['01']

# import default workflows
imported_workflows = {}
for module in settings['workflows']:
    imported_workflows[module] = importlib.import_module('{}.workflow'.format(module))

class test(unittest.TestCase):
    def test_generate_subworkflows(self):
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
        self.assertEqual(
            keys,[key for key in subworkflows]
        )
    def test_generate_connections(self):
        # generate subworkflows
        subworkflows = generate_subworkflows(imported_workflows,settings)
        # generate connections
        connections = generate_connections(subworkflows,settings)
        links = [(connect[0].fullname,connect[1].fullname) for connect in connections]
        # get connections from settings
        setting_links = [(entry['source'],entry['destination']) for entry in settings['connections']]
        for link in links:
            self.assertIn(link,setting_links)
    def test_sideload_nodes(self):
        # set sideload
        settings['sideload'] = [
            {
                'workflow': 'p3_bidsselector',
                'node': 'input',
                'input': ['subject','test']
            }
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
        # check sideloaded field
        sideload = settings['sideload'][0]
        field = p3.get_node('{}.{}'.format(sideload['workflow'],sideload['node'])).inputs.subject
        self.assertEqual(field,'test')
        
if __name__ == '__main__':
    unittest.main()
