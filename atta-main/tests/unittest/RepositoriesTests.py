import unittest
import sys

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
    p1 = PackageId.FromStr('artifactId.type:ver')
    self.assertEqual(str(p1), 'artifactId.type:ver')
    self.assertEqual(p1.groupId, p1.artifactId)

if __name__ == '__main__':
  unittest.main
