'''Filter task tests.'''
import os
import re
from atta import *

Project.defaultTarget = 'test'

class test(Target):
  def Run(self):
    Delete([DirSet(includes = '_test_filter*:_test_copy*:_test_move*'), '*.out'], 
           force = True, verbose = True)
  
    Echo('Simple contact files.')
    
    f = open('_test_filter.out', 'w')
    Filter(FileSet(includes = '**/*.py', excludes = '_test_filter/'), f, 
           failOnError = False)
    f.close()
    Filter(FileSet(includes = '**/*.py', excludes = '_test_filter/'), '_test_filter.out')

    Echo('Simple contact files in binary mode.')
    
    OS.Touch('_test_filter2.out')
    Filter(FileSet(includes = '**/*.py', excludes = '_test_filter/'), '_test_filter2.out', 
           binaryMode = True)
    f = open('_test_filter2.out', 'a+b')
    f.seek(26000)
    Filter(FileSet(includes = '**/*.py', excludes = '_test_filter/'), f, 
           append = False, binaryMode = True)
    f.close()
    
    Echo('Copy one file with data filter.')

    def SimpleDataFilter(data, **tparams):
      return data.replace('import', 'IMPORT')

    Filter('JavaMedium/main.java', '_test_filter/one_file/main_transformed.java', 
           destIsAFile = True, dataFilters = SimpleDataFilter, failOnError = False)
    
    Echo('Data filter for many files.')
    
    class DataFilter:
      def Start(self, srcFileName, destFileName, **tparams):
        Echo('Converting: %s to: %s' % (srcFileName, destFileName))
        
      def __call__(self, data, **tparams):
        return data.replace('public', 'PUBLIC')
      
      def End(self, **tparams):
        Echo('Success')
        
    Filter('JavaMedium/**/*.java', '_test_filter/filter', 
           dataFilters = [SimpleDataFilter, DataFilter()])
    
    Echo('Transform, change file names.')

    def FlattenFileName(srcRootDirName, srcFileName, 
                          destDirName, actualDestFileName, **tparams):
      rc = os.path.join( destDirName, os.path.basename(srcFileName) )
      Echo('Changing file name from: %s to: %s' % (actualDestFileName, rc))
      return rc
    
    def ChangeToPy(srcRootDirName, srcFileName, 
                     destDirName, actualDestFileName, **tparams):
      rc = re.sub('(.*\.)(java)$', (lambda m: m.group(1) + 'py'), actualDestFileName)
      Echo('Changing file name from: %s to: %s' % (actualDestFileName, rc))
      return rc
    
    Filter('JavaMedium/**/*.java', '_test_filter/filter2', 
           fileNameTransforms = [FlattenFileName, ChangeToPy])
  
    Echo('Filter files.')

    def FileFilter(srcFileName, destFileName, **tparams):
      return srcFileName.find('main') < 0
      
    Filter('JavaMedium/**/*.java', '_test_filter/filter3', 
           fileFilters = [FileFilter])
    
