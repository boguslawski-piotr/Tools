import unittest
import sys
import os

sys.path.insert(0, '../..')
from atta.repositories.Package import PackageId

class RepositoriesTests(unittest.TestCase):
  def setUp(self):
    pass

  def test_PackageId(self):
    p1 = PackageId('groupId', 'artifactId', 'ver', 'type')
    self.assertEqual(str(p1), 'groupId:artifactId.type:ver')
    p2 = PackageId.FromStr('groupId:artifactId.type:ver')
    self.assertEqual(p1, p2)

if __name__ == '__main__':
  unittest.main
