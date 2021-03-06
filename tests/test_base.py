#!/usr/bin/env python3
import unittest
from p3.base import *
from p3.settings import default_preproc_settings
from nipype import Node,Workflow
import tempfile

class test(unittest.TestCase):
    def test_basenodedefs(self):
        settings = default_preproc_settings()
        settings['output_dir'] = tempfile.TemporaryDirectory().name
        dn = basenodedefs(settings)
        self.assertIsInstance(
            dn,
            basenodedefs
        )
        dn.set_input(['test'])
        self.assertIsInstance(
            dn.inputnode,
            Node
        )
        dn.set_output(['test'])
        self.assertIsInstance(
            dn.outputnode,
            Node
        )
        dn.set_subs([
            ('_test1','_test2')
        ])
        dn.set_resubs([
            (r'_test\d{1,3}','_test'),
        ])
        self.assertIsInstance(
            dn.datasink,
            Node
        )
    def test_workflowgnerator(self):
        settings = default_preproc_settings()
        settings['tmp_dir'] = tempfile.TemporaryDirectory().name
        workflowgenerator('test',settings)
        self.assertIsInstance(
            workflowgenerator.workflow,
            Workflow
        )

if __name__ == '__main__':
    unittest.main()
