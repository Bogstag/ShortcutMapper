"""SHMAPlib is short for "Shortcut Mapper Lib". 
It's a Python library that will help you export data in the right format to the right location.
"""
import sys
import os

from .appdata import Shortcut, ShortcutContext, ApplicationConfig
from .keynames import get_all_valid_keynames, get_valid_keynames, is_valid_keyname
from .logger import getlog, setuplog
from .constants import DIR_ROOT, DIR_SOURCES, DIR_CONTENT_GENERATED, DIR_CONTENT_KEYBOARDS
from .intermediate import IntermediateShortcutData, IntermediateDataExporter

sys.path.append(os.path.dirname(__file__))
