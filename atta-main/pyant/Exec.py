## \package Exec 
#  \brief   Exec task 
#  \ingroup Tasks 
#
# \task{Exec(executable[, params, **tparams])}
#
# \param  executable The command to execute without any command line arguments.
#                    \type string 
#
# \copydoc ExecTaskFamilyParams
#  
# \uc exec.py
#
# \impl{pyant.Exec.Exec}
#
# \todo 
# Read stdout during the execution process \n
# Allow transfer of new environment variables to the process \n
# Parameters: os and osFamily \n
# Delete last empty line from output (?) \n
#
# \author Piotr Boguslawski (boguslawski.piotr@gmail.com)
#
# \example exec.py
# Exec task use cases.

## \defgroup ExecTaskFamilyParams Common parameters: Exec tasks family
# @{
# \param  params     Command line arguments.
#                    \type list of strings
#                    \def empty
#
# \tparam failOnError
# \tparam logOutput
# \tparam useSheel 
# @}

import io
import sys
import os
import subprocess
from pyant.BaseClasses import Task
from pyant.Log import LogLevel

## Exec task implementation
class Exec(Task):
  def __init__(self, executable, params = [], **tparams):  
    failOnError = tparams.get('failOnError', True)
    logOutput = tparams.get('logOutput', True)
    useShell = tparams.get('useShell', True)
    
    _output = ''
    _rc = 0
    try:
      _params = [executable]
      for param in params:
        _params.append(param)
      _output = subprocess.check_output(_params, env = os.environ, shell = useShell, stderr = subprocess.STDOUT)
    except subprocess.CalledProcessError, e:
      _output = e.output
      _rc = e.returncode
      if failOnError:
        self.Log(_output, level=LogLevel.ERROR)
        self._LogReturnCode(_rc, level=LogLevel.ERROR)
        raise
      
    if logOutput:
      self.Log(_output)
      self._LogReturnCode(_rc)
    
    self.returnCode = _rc
    self.output = _output

  ## \privatesection
  
  def _LogReturnCode(self, _rc, **args):
    if _rc > 0:
      self.Log('exit code: {0}'.format(_rc), **args)

