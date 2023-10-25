""" Keyboard tests
"""
import glob
import os
import re
import sys

import shmaplib
from tests.utils import BaseTestCase

# import our data common utility
sys.path.insert(0, os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..')))


class TestKeyboardLayout(BaseTestCase):
    """TestKeyboardLayout _summary_

    Args:
        BaseTestCase (_type_): _description_
    """

    def setup(self):
        self.valid_keys = shmaplib.get_all_valid_keynames()
        self.keyboard_templates = glob.glob(
            os.path.join(shmaplib.DIR_CONTENT_KEYBOARDS, '*.html'))

    def test_validate_keyboard_template_keynames(self):
        """test_validate_keyboard_template_keynames _summary_
        """
        print('\n')
        for p in self.keyboard_templates:
            print("   " + p)
            with open(p, 'r', encoding="utf-8") as template_file:
                contents = template_file.read()
                key_names = re.findall(r'.*button data-key="(.*?)"', contents)
                for keyname in key_names:
                    self.assert_in(keyname, self.valid_keys)
