#!/usr/bin/env python3
import unittest
from p3.workflows.p3_freesurfer.custom import *
import os

class test(unittest.TestCase):
    def test_gett1name(self):
        t1name = gett1name('test/test/test.nii.gz')
        self.assertEqual(t1name,'test')

if __name__ == '__main__':
    unittest.main()
