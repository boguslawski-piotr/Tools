import unittest
import sys

sys.path.insert(0, '../..')
import atta.tools.OS as OS

class OSTests(unittest.TestCase):
  def setUp(self):
    pass

  def test_OS_Path_Ext(self):
    self.assertTrue(OS.Path.Ext('1.log') == 'log')
    self.assertTrue(OS.Path.Ext('1') == '')
    self.assertTrue(OS.Path.Ext('1.xx.zzz.log') == 'log')

  def test_OS_Path_RemoveExt(self):
    self.assertTrue(OS.Path.RemoveExt('1.log') == '1')
    self.assertTrue(OS.Path.RemoveExt('1') == '1')
    self.assertTrue(OS.Path.RemoveExt('1.2.log') == '1.2')

  def test_OS_Path_HasWildcards(self):
    self.assertFalse(OS.Path.HasWildcards('1.log'))
    self.assertFalse(OS.Path.HasWildcards('.log'))
    self.assertFalse(OS.Path.HasWildcards('log'))
    self.assertTrue(OS.Path.HasWildcards('*.log'))
    self.assertTrue(OS.Path.HasWildcards('*'))
    self.assertTrue(OS.Path.HasWildcards('**/a'))
    self.assertTrue(OS.Path.HasWildcards('a?'))

  def test_OS_Path_HasAntStyleWildcards(self):
    self.assertFalse(OS.Path.HasAntStyleWildcards('1.log'))
    self.assertFalse(OS.Path.HasAntStyleWildcards('?a'))
    self.assertFalse(OS.Path.HasAntStyleWildcards('*/*'))
    self.assertTrue(OS.Path.HasAntStyleWildcards('**'))
    self.assertTrue(OS.Path.HasAntStyleWildcards('/**'))
    self.assertTrue(OS.Path.HasAntStyleWildcards('/**/a/b/c/**'))

  def test_OS_Path_Math(self):
    self.assertTrue(OS.Path.Match('*.log', 'AqC.log'))
    self.assertTrue(OS.Path.Match('**/*.log', 'AqC.log'))
    self.assertTrue(OS.Path.Match('**/*.log', 'ala/ma/kota/Test/std/AqC.log'))
    self.assertFalse(OS.Path.Match('*.log', 'test/AqC.log'))
    self.assertFalse(OS.Path.Match('*.log', 'ala/ma/kota/Test/std/AqC.log'))

    self.assertTrue(OS.Path.Match('**/*', 'ala/ma/kota/Test/std/AqC.log'))
    self.assertTrue(OS.Path.Match('**/*', 'ala/ma/kota/Test/std/dir'))
    self.assertTrue(OS.Path.Match('**/*', 'dir'))
    self.assertTrue(OS.Path.Match('**', 'dir'))
    self.assertTrue(OS.Path.Match('*', 'dir'))
    self.assertTrue(OS.Path.Match('**/std/A*.log', 'ala/ma/kota/Test/std/AqC.log'))
    self.assertFalse(OS.Path.Match('**/std/*/*.log', 'ala/ma/kota/Test/std/AqC.log'))
    self.assertTrue(OS.Path.Match('**/std/**/*.log', 'ala/ma/kota/Test/std/AqC.log'))

    self.assertTrue(OS.Path.Match('**/kota/**/', 'ala/ma/kota/Test/std/AqC.log'))
    self.assertTrue(OS.Path.Match('**', 'ala/ma/kota/Test/std/AqC.log'))
    self.assertTrue(OS.Path.Match('ala/ma/**', 'ala/ma/kota/Test/std/AqC.log'))
    self.assertTrue(OS.Path.Match('ala/*/ko*/*/**', 'ala/ma/kota/Test/std/AqC.log'))

    self.assertFalse(OS.Path.Match('**/i**/*.py', 'build.py'))
    self.assertTrue(OS.Path.Match('**/i**/*.py', 'foo/ham/int/build.py'))
    self.assertTrue(OS.Path.Match('**/build', 'docs/html/build'))
    self.assertFalse(OS.Path.Match('**/build', 'docs/.build'))

    self.assertTrue(OS.Path.Match('_test_filter/**', '_test_filter/.build'))
    self.assertFalse(OS.Path.Match('_test_filter/**', '_test_filter2/.build'))

    self.assertTrue(OS.Path.Match('**/CVS/*', 'CVS/Repository'))
    self.assertTrue(OS.Path.Match('**/CVS/*', 'org/apache/CVS/Entries'))
    self.assertTrue(OS.Path.Match('**/CVS/*', 'org/apache/jakarta/tools/ant/CVS/Entries'))
    self.assertFalse(OS.Path.Match('**/CVS/*', 'org/apache/CVS/foo/bar/Entries'))

    self.assertTrue(OS.Path.Match('org/apache/jakarta/**', 'org/apache/jakarta/tools/ant/docs/index.html'))
    self.assertTrue(OS.Path.Match('org/apache/jakarta/**', 'org/apache/jakarta/test.xml'))
    self.assertFalse(OS.Path.Match('org/apache/jakarta/**', 'org/apache/xyz.java'))

    self.assertTrue(OS.Path.Match('org/apache/**/CVS/*', 'org/apache/CVS/Entries'))
    self.assertTrue(OS.Path.Match('org/apache/**/CVS/*', 'org/apache/jakarta/tools/ant/CVS/Entries'))
    self.assertFalse(OS.Path.Match('org/apache/**/CVS/*', 'org/apache/CVS/foo/bar/Entries'))

    self.assertFalse(OS.Path.Match('**/test/**', 'org/apache/CVS/Entries/test.a'))
    self.assertTrue(OS.Path.Match('**/test/**', 'org/apache/test/CVS/Entries/a.a'))
    self.assertFalse(OS.Path.Match('**/test/**', 'test.a'))
    self.assertFalse(OS.Path.Match('**/test/**', 'test_move.py'))
    self.assertTrue(OS.Path.Match('**/test/', 'test/.a'))

    self.assertTrue(OS.Path.Match('te??/*', 'test/.a'))
    self.assertTrue(OS.Path.Match('te**/*.a', 'test/.a'))
    self.assertFalse(OS.Path.Match('te**/*a?', 'test/.a'))

    self.assertFalse(OS.Path.Match('te.+/.*a.{1,1}', 'test/.a', True))
    self.assertTrue(OS.Path.Match('te.{1,1}.{1,1}/.*', 'test/.a', True))

    self.assertTrue(OS.Path.Match('org/atta/tests/**', 'org/atta/tests/inc/inc2/something'))
    self.assertTrue(OS.Path.Match('org/atta/tests/**', 'org/atta/tests/test.xml'))
    self.assertFalse(OS.Path.Match('org/atta/tests/**', 'org/atta/xyz.java'))

if __name__ == '__main__':
  unittest.main
