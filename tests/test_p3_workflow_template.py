#!/usr/bin/env python3
import unittest
from p3.workflows.workflow_template import workflow,nodedefs
from p3.settings import default_preproc_settings
from nipype import Workflow
import os
import tempfile

class test(unittest.TestCase):
    def test_nodedefs(self):
        # get settings
        settings = default_preproc_settings()
        settings['output_dir'] = tempfile.TemporaryDirectory().name
        # define node object
        defnodeobj = nodedefs.definednodes(settings)
        # assert the instance
        self.assertIsInstance(defnodeobj,nodedefs.definednodes)

    def test_workflow(self):
        # get settings
        settings = default_preproc_settings()
        settings['tmp_dir'] = tempfile.TemporaryDirectory().name
        settings['output_dir'] = tempfile.TemporaryDirectory().name
        gen_wf = workflow.newworkflow('test',settings)
        self.assertIsInstance(
            gen_wf,
            Workflow
        )

if __name__ == '__main__':
    unittest.main()
