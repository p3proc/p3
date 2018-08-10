#!/usr/bin/env python3
import sys
sys.path.append("..")
import unittest
from p3.utility import *
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
        manual_path = os.path.abspath("../p3/templates/MNI152.nii.gz")
        self.assertEqual(
            set_atlas_path(
                "MNI152.nii.gz"
            ),
            manual_path
        )

if __name__ == '__main__':
    unittest.main()
