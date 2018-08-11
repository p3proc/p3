#!/usr/bin/env python3
import unittest
from p3.workflows.p3_alignfunctoanat.custom import *
import os

class test(unittest.TestCase):
    def test_get_prefix(self):
        basename = get_prefix('test/test/test.nii.gz')
        self.assertEqual(basename,'test')

if __name__ == '__main__':
    unittest.main()
