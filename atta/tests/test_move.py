"""Copy task tests."""
from atta import *

Project.defaultTarget = 'test'

class test(Target):
  def Run(self):
    Delete([DirSet(includes = '_test_copy*:_test_move*'), '*.out'],
           force = True)
    Copy('JavaBasic/**/*', destDirName = '_test_copy3',
         verbose = False)
    Copy('JavaBasic/**/*', destDirName = '_test_copy4',
         verbose = False)

    Echo('Simple move.')
    Move(FileSet('_test_copy3', includes='**/*'), destDirName = '_test_move',
         overwrite = True, force = True, verbose = True)
    Move('_test_copy4/**/*', destDirName = '_test_move2',
         verbose = True)
