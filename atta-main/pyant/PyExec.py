## \package PyExec 
#  \brief   PyExec task 
#  \ingroup Tasks 
#
# \task{PyExec(fileName[, params, **tparams])}
#
# \param  fileName The file name of the program in Python.
#                  \type string 
#  
# \copydoc ExecTaskFamilyParams
#
# \uc pyexec.py
#
# \impl{pyant.PyExec.PyExec}
#
# \author Piotr Boguslawski (boguslawski.piotr@gmail.com)
#
# \example pyexec.py
# PyExec task use cases.

import sys
import os
from pyant.Exec import Exec
from pyant.Log import LogLevel
from pyant.OS import Ext

class PyExec(Exec):
  def __init__(self, fileName, params = [], **tparams):  
    if Ext(fileName) == '':
      fileName = fileName + '.py' 
    
    if fileName.find(os.path.sep) == -1:
      for path in sys.path:
        _fileName = os.path.join(path, fileName)
        if os.path.exists(_fileName):
          fileName = _fileName
    
    params.insert(0, fileName)
    Exec.__init__(self, 'python', params, **tparams)
