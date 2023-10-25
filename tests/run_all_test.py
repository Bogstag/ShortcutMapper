""" Run all tests
"""
import unittest

from tests.keyboards_test import TestKeyboardLayout


def main():
    """
    Runs the testsuite as command line application, or... that's what it will eventually do.
    For the moment, just run everything
    """

    try:
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestKeyboardLayout))

        unittest.TextTestRunner(verbosity=2).run(suite)

    except Exception as e:
        print(f'Error: {e}')


if __name__ == '__main__':
    main()
