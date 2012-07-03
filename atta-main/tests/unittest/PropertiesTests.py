import unittest
import sys
import os

sys.path.insert(0, '../..')
from atta.tools.Properties import Properties

class PropertiesTests(unittest.TestCase):
  def setUp(self):
    pass

  def test_Properties(self):
    p = Properties.Create('test.properties')
    p.Set('test', 'something')
    p.Set('test2', 17)
    p.Save()

    p1 = Properties.Open('test.properties')
    test = p1.Get('test', 'WRONG!')
    test2 = p1.Get('test2', None)
    
    self.assertEqual(test, 'something')
    self.assertEqual(long(test2), 17)
    
    os.remove('test.properties')
    
if __name__ == '__main__':
  unittest.main
    