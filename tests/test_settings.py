#!/usr/bin/env python3
import unittest
from p3.settings import *

class test(unittest.TestCase):
    def test_default_preproc_settings(self):
        settings = default_preproc_settings()
        self.assertEqual(
            settings['atlas'],
            'MNI152.nii.gz'
        )

if __name__ == '__main__':
    unittest.main()
