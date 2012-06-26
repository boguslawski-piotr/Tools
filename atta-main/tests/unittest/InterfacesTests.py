import unittest
import sys
import os
from atta.Interfaces import IRepository

sys.path.insert(0, '../..')
import atta.Interfaces

class InterfacesTests(unittest.TestCase):
  def setUp(self):
    pass

  def test_IRepository(self):
    self.assertEqual(IRepository.ResolveDisplayName('groupId:artifactId.type:ver'), ('groupId', 'artifactId', 'type', 'ver'))
    self.assertEqual(IRepository.ResolveDisplayName('artifactId.type:ver'), ('artifactId', 'artifactId', 'type', 'ver'))
    self.assertEqual(IRepository.ResolveDisplayName('artifactId.type'), ('artifactId', 'artifactId', 'type', ''))
    self.assertEqual(IRepository.ResolveDisplayName('artifactId'), ('artifactId', 'artifactId', '', ''))
    self.assertEqual(IRepository.ResolveDisplayName(''), ('', '', '', ''))
    self.assertEqual(IRepository.ResolveDisplayName(dict()), ('', '', '', ''))

if __name__ == '__main__':
  unittest.main
    