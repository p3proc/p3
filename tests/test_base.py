#!/usr/bin/env python3
import sys
sys.path.append("..")
import unittest
from p3.base import *
from p3.settings import default_preproc_settings
from nipype import Node

class test(unittest.TestCase):
    def test_basenodedefs(self):
        settings = default_preproc_settings()
        settings['output_dir'] = './'
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

if __name__ == '__main__':
    unittest.main()
