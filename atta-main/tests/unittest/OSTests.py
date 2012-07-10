import unittest
import sys
import os

sys.path.insert(0, '../..')
import atta.tools.OS as OS

class OSTests(unittest.TestCase):
  def setUp(self):
    pass

  def test_OS_Ext(self):
    self.assertTrue(OS.Path.Ext('1.log') == 'log')
    self.assertTrue(OS.Path.Ext('1') == '')
    self.assertTrue(OS.Path.Ext('1.xx.zzz.log') == 'log')

  def test_OS_RemoveExt(self):
    self.assertTrue(OS.Path.RemoveExt('1.log') == '1')
    self.assertTrue(OS.Path.RemoveExt('1') == '1')
    self.assertTrue(OS.Path.RemoveExt('1.2.log') == '1.2')

if __name__ == '__main__':
  unittest.main
