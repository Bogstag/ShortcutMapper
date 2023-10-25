""" _summary_
"""
import os
import sys

import shmaplib
import tests

# Add root dir to PATH env var
CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CWD)
sys.path.insert(0, os.path.normpath(os.path.join(CWD, '..')))


shmaplib.setuplog()

if __name__ == '__main__':
    tests.main()
