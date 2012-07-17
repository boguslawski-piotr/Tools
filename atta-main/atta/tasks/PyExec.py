""".. Execution: Executes Python program: pyexec"""
import sys
import os

from .. import LogLevel, OS
from .Exec import Exec

class PyExec(Exec):
  """
  Executes Python program.

  TODO: detailed information

  Parameter:

  * **fileName** The file name of the program in Python.

  Other parameters and ... TODO are exactly the same
  as in :py:class:`.Exec`.

  """
  def __init__(self, fileName, params = None, **tparams):
    if len(fileName) > 0 and not fileName.startswith('-'):
      if OS.Path.Ext(fileName) == '':
        fileName += '.py'

      if fileName.find(os.path.sep) == -1:
        for dirName in sys.path:
          _fileName = os.path.join(dirName, fileName)
          if os.path.exists(_fileName):
            self.Log('Found {0} in: {1}'.format(fileName, dirName), level = LogLevel.VERBOSE)
            fileName = _fileName
            break

    _params = OS.Path.AsList(params)
    _params.insert(0, fileName)
    Exec.__init__(self, 'python', _params, **tparams)
