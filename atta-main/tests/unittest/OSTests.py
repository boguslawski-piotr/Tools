import unittest
import sys
sys.path.insert(0, '../..')
from atta.tools.OS import Ext, RemoveExt

class OSTests(unittest.TestCase):
  def setUp(self):
    pass

  def test_OS_Ext(self):
    self.assertTrue( Ext('1.log') == 'log' )
    self.assertTrue( Ext('1') == '' )
    self.assertTrue( Ext('1.xx.zzz.log') == 'log' )

  def test_OS_RemoveExt(self):
    self.assertTrue( RemoveExt('1.log') == '1' )
    self.assertTrue( RemoveExt('1') == '1' )
    self.assertTrue( RemoveExt('1.2.log') == '1.2' )

if __name__ == '__main__':
    unittest.main
    