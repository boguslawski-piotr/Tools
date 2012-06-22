'''
  .. snippet:: PyExec
  
    .. code-block:: python

      PyExec(fileName[, params, **tparams])}

    Executes Python program. 

  .. snippetref:: ExecAdditionalInfo
  
  .. snippet:: PyExecParams

    :param string fileName: The file name of the program in Python.

  .. snippetref:: ExecCommonParams
  .. snippetref:: ExecReturns

  .. snippet:: PyExecUseCases
  
    Use cases:
    
    .. literalinclude:: ../../../tests/test_pyexec.py

  .. codeauthor:: Piotr Boguslawski <boguslawski.piotr@gmail.com>
  '''
import sys
import os

from Exec import Exec
from ..Log import LogLevel
from ..tools.OS import Ext

class PyExec(Exec):
  def __init__(self, fileName, params = [], **tparams):  
    if len(fileName) > 0 and not fileName.startswith('-'):
      if Ext(fileName) == '':
        fileName = fileName + '.py' 
      
      if fileName.find(os.path.sep) == -1:
        for path in sys.path:
          _fileName = os.path.join(path, fileName)
          if os.path.exists(_fileName):
            fileName = _fileName
    
    params.insert(0, fileName)
    Exec.__init__(self, 'python', params, **tparams)
