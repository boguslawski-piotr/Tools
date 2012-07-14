'''Filter task tests.'''
import os
import re
from atta import *

Project.defaultTarget = 'test'

class test(Target):
  def Run(self):
    Delete([DirSet(includes = '_test_filter*/**'), '*.out'], 
           force = True, verbose = True)
    Copy('JavaBasic/**/*', destDirName = '_test_filter', 
         failOnError = False, verbose = False)
  
    def SimpleDataFilter(data, **tparams):
      rc = data.replace('import', 'IMPORT')
      if data != rc:
        tparams['caller'].Log('Changed: %s to: %s' % (data.rstrip(), rc.rstrip()))
      return rc
    
    Echo()
    Echo('Copy one file with data filter.')
    
    Filter('JavaMedium/main.java', destFile = '_test_filter/one_file/main_transformed.java', 
           dataFilters = SimpleDataFilter, failOnError = False)

    Echo()
    Echo('In-place filters 1.')

    Filter(FileSet('_test_filter/JavaBasic', includes='**/*.java:**/*.py'),  
           dataFilters = SimpleDataFilter)
    
    Echo()
    Echo('In-place filters 2.')

    Echo('''This is a \${test}.''',
         file = '_test_filter/test.txt')
    OS.SetReadOnly('_test_filter/test.txt', True)
    Echo(OS.LoadFile('_test_filter/test.txt'), expandVars = False)
    
    class Replace:
      def __init__(self, what, to):
        self.what = what
        self.to = to
      def __call__(self, data, **tparams):
        return data.replace(self.what, self.to)
    
    class RegExReplace:
      def __init__(self, regex, to, count = 0):
        if isinstance(regex, basestring):
          self.regex = re.compile(regex)
        else:
          self.regex = regex 
        self.to = to
        self.count = count
      def __call__(self, data, **tparams):
        return self.regex.sub(self.to, data, self.count)

    class ExpandVars:
      def __init__(self, **tparams):
        self.tparams = tparams
      def __call__(self, data, **tparams):
        return Atta.ExpandVars(data, **self.tparams)
        
    Filter('_test_filter/test.txt', dataFilters = Replace('test', 'ham'), force = True)
    Echo(OS.LoadFile('_test_filter/test.txt'), expandVars = False)
    
    Filter('_test_filter/test.txt', dataFilters = ExpandVars(ham = 'foo'))
    Echo(OS.LoadFile('_test_filter/test.txt'), expandVars = False)
    
    Filter('_test_filter/test.txt', dataFilters = RegExReplace('.*(\sis\s).*', (lambda m: m.group(0).replace(m.group(1), ' was '))))
    Echo(OS.LoadFile('_test_filter/test.txt'), expandVars = False)
    
    Filter('_test_filter/test.txt', dataFilters = RegExReplace(re.compile('\swas\s'), ' will be '))
    Echo(OS.LoadFile('_test_filter/test.txt'), expandVars = False)        
