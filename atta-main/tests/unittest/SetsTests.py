import unittest
import sys
sys.path.insert(0, '../..')
from atta import FileSet

class FileSetTests(unittest.TestCase):
  def setUp(self):
    pass

  def test_FileSet_Math(self):
    self.assertTrue(  FileSet.Match('*.log', 'AqC.log') )
    self.assertTrue(  FileSet.Match('**/*.log', 'AqC.log') )
    self.assertTrue(  FileSet.Match('**/*.log', 'ala/ma/kota/Test/std/AqC.log') )
    self.assertFalse( FileSet.Match('*.log', 'test/AqC.log') )
    self.assertFalse( FileSet.Match('*.log', 'ala/ma/kota/Test/std/AqC.log') )
    
    self.assertFalse( FileSet.Match('**/std/*/*.log', 'ala/ma/kota/Test/std/AqC.log') )
    self.assertTrue(  FileSet.Match('**/std/**/*.log', 'ala/ma/kota/Test/std/AqC.log') ) 
    
    self.assertTrue(  FileSet.Match('**/kota/**/**', 'ala/ma/kota/Test/std/AqC.log') )
    self.assertTrue(  FileSet.Match('/', 'ala/ma/kota/Test/std/AqC.log') )

    self.assertFalse( FileSet.Match('**/i**/*.py', 'build.py') )
    self.assertTrue(  FileSet.Match('**/build', 'docs/html/build') )
    self.assertFalse( FileSet.Match('**/build', 'docs/.build') )

if __name__ == '__main__':
    unittest.main
    