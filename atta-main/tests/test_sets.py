'''Sets tests.'''
from atta import *

Project.defaultTarget = 'test'

class test(Target):
  def Run(self):
    Delete(DirSet(includes = '_test_filter*'), 
           force = True)
    
    OS.MakeDirs('_test_filter:_test_filter2')
    OS.Touch('_test_filter/1.py')
    OS.Touch('_test_filter2/1.py')
    
    Echo(FileSet(includes = '**/*1*.py', excludes = '_test_filter/'))

    Echo()
    Echo(len(FileSet('..', includes = '**/*')))
    Echo(len(FileSet('..', includes = '**/*', useDefaultExcludes = False)))
    
    Echo()
    Echo(DirFileSet('JavaBasic', includes = '**/src**/**'))
    
    Echo()
    Echo(FileSet('..', includes = '*.*'))