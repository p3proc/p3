#!/usr/bin/env python3
import unittest
from p3.utility import *
import p3
import os
from mock import patch
from .mock_stdout import MockDevice
current_dir = os.path.dirname(os.path.abspath(os.path.realpath(__file__))) # get the current directory

class test(unittest.TestCase):
    def test_get_basename(self):
        # Test basename retrival of filenames
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
        # Test getting an atlas path
        root_path = os.path.dirname(os.path.abspath(os.path.realpath(p3.__file__)))
        manual_path = os.path.join(root_path,"templates","MNI152.nii.gz")
        self.assertEqual(
            set_atlas_path(
                "MNI152.nii.gz"
            ),
            manual_path
        )
        # Test not getting an atlas path
        self.assertRaises(IOError,set_atlas_path,"test.nii.gz")

    def test_output_BIDS_summary(self):
        with patch('sys.stdout',new=MockDevice()) as fake_out:
            # test printing the bids summary
            output_BIDS_summary(os.path.join(current_dir,'example_data'))

if __name__ == '__main__':
    unittest.main()
