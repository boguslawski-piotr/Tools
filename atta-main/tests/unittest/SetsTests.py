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
    
'''

    #rootDir, fileSet = FileSet().MakeSet('.', '*.py?', False)
    #rootDir, fileSet = FileSet().MakeSet('.', 'tests/**/*.log', False)
    #rootDir, fileSet = FileSet().MakeSet('..', '**/std/**/*.log', False)
    #BAD!rootDir, fileSet = FileSet().MakeSet('.', '**/i**/*.py', False)
    #rootDir, fileSet = FileSet().MakeSet('atta', 'templates/T*.py', False)
    #rootDir, fileSet = FileSet().MakeSet('atta', '*.py')
    #rootDir, fileSet = FileSet().MakeSet('atta', '**/*.py', '__*')
    
    for name in FileSet(includes = 'build*'):
      print name 
#    for name in FileSet('.', '**/**', '.git/'):
#      print name 
    x = DirSet('.', '**/*t*', '.git/')
    print len(x)
    for name in x:
      print name 
    return  

    for name in FileSet(includes = '**/*.py'):
      print name 
    return
  
'''
    