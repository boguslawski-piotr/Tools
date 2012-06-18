## \brief Echo task tests.

from atta import *
import os
import stat
import atta.OS

Project.defaultTarget = 'test'

class test(Target):
  def Run(self):
    Echo('One line')
    Echo('''Multi
line''')
    Echo('Multi' + os.linesep + 'line 2')
    
    Echo()
    
    Echo('only debug', level = LogLevel.DEBUG)
    Echo('debug, verbose', level = LogLevel.VERBOSE)
    Echo('debug, verbose, info', level = LogLevel.INFO)
    Echo('debug, verbose, info, warning', level = LogLevel.WARNING)
    Echo('always', level = LogLevel.ERROR)
    
    Echo()
    
    testFileName = 'echo.log'
    
    # prepare file for test:
    if os.path.exists(testFileName): os.chmod(testFileName, stat.S_IWRITE)
    with open(testFileName, 'w+') as f:
      f.write('1234567890')
    os.chmod(testFileName, stat.S_IREAD)
    # :prepare
    
    Echo('file test', file = testFileName, force = True)
    Echo('file test 2', file = testFileName, append = True)
    
    with open(testFileName, 'r+') as f:
      Echo('file test 3', file = f)
    with open(testFileName, 'r+') as f:
      Echo('file test 4', append = True, file = f)

    with open(testFileName, 'r') as f:
      Echo(f.read())
      
