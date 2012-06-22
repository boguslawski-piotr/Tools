import unittest
import sys
sys.path.insert(0, '../..')
from atta.tools.Misc import ExpandVariables

funny = 'funny'

class ExpandVariablesTests(unittest.TestCase):
  def setUp(self):
    pass

  def test_ExpandVariables(self):
    txt = 'The Atta is ${what} and ${MiscTests.funny}.'
    txt = ExpandVariables(txt, what = 'cool')
    self.assertTrue( 'The Atta is cool and funny.' == txt )

if __name__ == '__main__':
  unittest.main
    