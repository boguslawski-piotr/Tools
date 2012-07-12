'''Filter task tests.'''
import os
import re
from atta import *

Project.defaultTarget = 'test'

class test(Target):
  def Run(self):
    Delete([DirSet(includes = '_test_filter*'), '*.out'], verbose = True)
    return
  
    def SimpleDataFilter(data):
      return data.replace('import', 'IMPORT')
    
    class DataFilter:
      def Start(self, srcFileName, destFileName):
        Echo('Converting: %s to: %s' % (srcFileName, destFileName))
        
      def __call__(self, data):
        return data.replace('public', 'PUBLIC')
      
      def End(self):
        Echo('Success')
        
    Filter('JavaMedium/**/*.java', '_test_filter/filter', dataFilters = [SimpleDataFilter, DataFilter()])
#    return
    
    def FlattenFileName(srcRootDirName, srcFileName, destDirName, actualDestFileName):
      return os.path.join( destDirName, os.path.basename(srcFileName) )
    
    def ChangeToPy(srcRootDirName, srcFileName, destDirName, actualDestFileName):
      return re.sub('(.*\.)(java)$', (lambda m: m.group(1) + 'py'), actualDestFileName)
    
    Filter('JavaMedium/**/*.java', '_test_filter/filter2', fileNameTransforms = [FlattenFileName, ChangeToPy])
    return
  
    Echo('Simple copy files.')
    Filter('**/*.py', '_test_filter')
    
    Echo('Simple contact files.')
    f = open('_test_filter.out', 'w')
    Filter(FileSet(includes = '**/*.py', excludes = '_test_filter/'), f)
    f.close()
    Filter(FileSet(includes = '**/*.py', excludes = '_test_filter/'), '_test_filter.out')

    Echo('Simple copy files in binary mode.')
    Filter(FileSet(includes = '**/*.py', excludes = '_test_filter/', realPaths = False), '_test_filter2', binaryMode = True)
  
    Echo('Simple contact files in binary mode.')
    OS.Touch('_test_filter2.out')
    Filter(FileSet(includes = '**/*.py', excludes = '_test_filter/'), '_test_filter2.out', binaryMode = True)
    f = open('_test_filter2.out', 'a+')
    Filter(FileSet(includes = '**/*.py', excludes = '_test_filter/'), f, binaryMode = True)
    f.close()
    
    
    
    # TODO: PROBLEM
    #FileSet(includes = '**/*.py', excludes = '_test_filter/')
    # why this above cut also _test_filter2?