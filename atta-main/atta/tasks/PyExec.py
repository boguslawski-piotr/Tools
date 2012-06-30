'''.. Execution: Executes Python program: pyexec'''
import sys
import os

from Exec import Exec
from ..tools.Misc import LogLevel
import atta.tools.OS as OS

class PyExec(Exec):
  '''
  Executes Python program. 

  TODO: detailed information

  Parameter:
  
  * **fileName** The file name of the program in Python.
  
  Other parameters and ... TODO are exactly the same 
  as in :py:class:`.Exec`.

  '''
  def __init__(self, fileName, params = [], **tparams):  
    if len(fileName) > 0 and not fileName.startswith('-'):
      if OS.Path.Ext(fileName) == '':
        fileName = fileName + '.py' 
      
      if fileName.find(os.path.sep) == -1:
        for path in sys.path:
          _fileName = os.path.join(path, fileName)
          if os.path.exists(_fileName):
            self.Log('Found {0} in: {1}'.format(fileName, path), level = LogLevel.VERBOSE)
            fileName = _fileName
            break
    
    params.insert(0, fileName)
    Exec.__init__(self, 'python', params, **tparams)
