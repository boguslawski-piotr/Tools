#!/usr/bin/python

## \brief  atta main
#  \author Piotr Boguslawski (boguslawski.piotr@gmail.com)

import sysconfig
import sys
import os

from atta.Atta import Atta
from atta.Log import LogLevel, Log, LoggerBridge
import atta

minPythonVersion = '2.7'

def Main():
  if LoggerBridge.LoggerClass is None:
    LoggerBridge.LoggerClass = atta.StdLogger.Logger

  try:
    if int(sysconfig.get_python_version().replace('.', '')) < int(minPythonVersion.replace('.', '')):
      raise SystemError('Wrong version of Python. Requires {0} and {1} were detected.'.format(minPythonVersion, sysconfig.get_python_version()))
     
    _atta = Atta(os.environ,
                 os.path.dirname(os.path.realpath(sys.argv[0])), 
                 sys.argv[1:])
    _atta.Run()
    return 0
  
  except Exception, e:
    if LogLevel.actual <= LogLevel.VERBOSE:
      raise
    else:
      Log(e, level = LogLevel.ERROR)
      return 1
    
if __name__ == "__main__":
  sys.exit(Main())


#  buildFile = open(Project.buildFile, 'r')
#  script = ''
#  for line in buildFile.readlines():
#    script = script + line + os.linesep
#  buildFile.close()
#  script = build.ParseScript(script)
#  exec(script)
  
