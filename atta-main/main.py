#!/usr/bin/python

## \brief  atta main
#  \author Piotr Boguslawski (boguslawski.piotr@gmail.com)

import platform
import sys
import os

from atta.Atta import Atta

def Main():
  minPythonVersion = '2.7.0'
  if int(platform.python_version().replace('.', '')) < int(minPythonVersion.replace('.', '')):
    # check Python version
    print('Wrong version of Python. Requires {0}+ and {1} were detected.'.format(minPythonVersion, platform.python_version()))
    return 1
  
  else:
    # run Atta
    _atta = Atta(os.environ,
                 os.path.dirname(os.path.realpath(sys.argv[0])), 
                 sys.argv[1:])
    return _atta.Run()
    
##
#
    
if __name__ == "__main__":
  sys.exit(Main())


#  buildFile = open(Project.buildFile, 'r')
#  script = ''
#  for line in buildFile.readlines():
#    script = script + line + os.linesep
#  buildFile.close()
#  script = build.ParseScript(script)
#  exec(script)
  
