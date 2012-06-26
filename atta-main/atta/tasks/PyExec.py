import sys
import os

from Exec import Exec
from ..tools.Misc import LogLevel
import atta.tools.OS as OS

class PyExec(Exec):
  '''
  .. snippet:: PyExec
  
    .. code-block:: python

      PyExec(fileName[, params, **tparams])}

    Executes Python program. 

  .. snippetref:: ExecAdditionalInfo
  
  .. snippet:: PyExecParams

    :param string fileName: The file name of the program in Python.

  .. snippetref:: ExecCommonParams
  .. snippetref:: ExecCommonParams2
  .. snippetref:: ExecReturns

  .. snippet:: PyExecUseCases
  
    Use cases:
    
    .. literalinclude:: ../../../tests/test_pyexec.py

  .. codeauthor:: Piotr Boguslawski <boguslawski.piotr@gmail.com>
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
