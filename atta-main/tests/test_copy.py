'''Copy task tests.'''
from atta import *

Project.defaultTarget = 'test'

class test(Target):
  def Run(self):
    Delete([DirSet(includes = '_test_copy*:_test_move*'), '*.out'], 
           force = True)
    
    Echo('Simple copy files.')
    Copy(FileSet('JavaBasic', includes='**/*'), '_test_copy', 
         overwrite = True, force = True)
    Copy('JavaBasic/**/*', '_test_copy2')
    
    Echo()
    Echo('Copy again using the time of last modification to compare files.')
    OS.Touch('JavaBasic/version.info')
    Echo('Touch JavaBasic/version.info')
    Copy('JavaBasic/**/*', '_test_copy2')
  
    Echo()
    Echo('Copy again using SHA1-hash to compare files.')
    OS.Touch('JavaBasic/version.info')
    Echo('Touch JavaBasic/version.info')
    Copy('JavaBasic/**/*', '_test_copy2', 
         useHash = True)
