#!/usr/bin/env python3
import unittest
from p3.utility import *
import p3
import os

class test(unittest.TestCase):
    def test_get_basename(self):
        self.assertEqual(
            get_basename(
                "test_test_test.nii.gz"
            ),
            "test_test_test"
        )
        self.assertEqual(
            get_basename(
                "dsfkjashdfkjasdfkh.nii"
            ),
            "dsfkjashdfkjasdfkh"
        )

    def test_set_atlas_path(self):
        root_path = os.path.dirname(os.path.abspath(os.path.realpath(p3.__file__)))
        manual_path = os.path.join(root_path,"templates","MNI152.nii.gz")
        self.assertEqual(
            set_atlas_path(
                "MNI152.nii.gz"
            ),
            manual_path
        )

if __name__ == '__main__':
    unittest.main()
