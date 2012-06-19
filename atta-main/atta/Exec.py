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
# \copydoc ExecTaskFamilyReturns
#  
# \todo 
# Add reading environment variable set by the executed process \n
# Parameters: os and osFamily \n
#
# \uc test_exec.py
# \uc test_env2.py
#
# \impl{atta.Exec.Exec}
#
# \author Piotr Boguslawski (boguslawski.piotr@gmail.com)
#
# \example test_exec.py
# Exec task use cases.
# \example test_env2.py
# Exec task and environments variables use cases.

## \defgroup ExecTaskFamilyParams Common parameters: Exec tasks family
# @{
# \param  params      Command line arguments.
#                     \type list of strings
#                     \def empty
#
# \tparam failOnError Stop the buildprocess if the command exits with a return code signaling failure.
#                     \type boolean
#                     \def True
# \tparam logOutput   \trans Przesyla stdout and stderr do logu Atta. 
#                     \type boolean
#                     \def True
# \tparam useSheel    Command will be executed through the shell. 
#                     More information can be found <a href="http://docs.python.org/library/subprocess.html?highlight=popen#subprocess.Popen">here.</a>
#                     \type boolean
#                     \def True
# \tparam env         Environment variables. Completely replace the variables from the project.
#                     \type dict
#                     \def None
# @}

## \defgroup ExecTaskFamilyReturns Common returns: Exec tasks family
# @{
# \return Object with two attributtes:
#         \rvalN returnCode Exit code returned by executed command.
#                           \type int
#         \rvalN output     Captured contents of stdout and stderr.
#                           \type string
#
# @}

import io
import sys
import os
import subprocess
import threading

import atta
from BaseClasses import Task
from Log import LogLevel

## Exec task implementation
class Exec(Task):
  def __init__(self, executable, params = [], **tparams):  
    failOnError = tparams.get('failOnError', True)
    self.logOutput = tparams.get('logOutput', True)
    useShell = tparams.get('useShell', True)
    env = tparams.get('env', None)
    
    _output = ''
    _rc = 0

    _params = [executable]
    for param in params:
      _params.append(param)
    if env is None:
      if atta.project is None:
        env = os.environ
      else:
        env = atta.project.env.vars
    
    process = subprocess.Popen(_params, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, 
                               bufsize = 1, env = env, shell = useShell)
    _output = self._communicate(process)
    _rc = process.poll()
    if _rc:
      if failOnError:
        if not self.logOutput:
          self.Log(_output, level = LogLevel.ERROR)
        self._LogReturnCode(_rc, level = LogLevel.ERROR)
        raise subprocess.CalledProcessError(_rc, _params, output = _output)
      
    if self.logOutput:
      self._LogReturnCode(_rc)
    
    self.returnCode = _rc
    self.output = _output

  ## \privatesection
  
  def _reader(self, fh, output):
    line = ''
    while True:
      _char = fh.read(1)
      if _char == '':
        break
      if _char != '\r':
        if _char != '\n':
          line = line + _char
        else:
          if self.logOutput:
            self.Log(line)
          output.append(line + os.linesep)
          line = ''

  def _communicate(self, process):
    stdout = []
    if process.stdout:
      stdout_thread = threading.Thread(target=self._reader,
                                       args=(process.stdout, stdout))
      stdout_thread.setDaemon(True)
      stdout_thread.start()
      stdout_thread.join()

    process.wait()
    
    stdout = ''.join(stdout)
    lastEOL = stdout.rfind(os.linesep)
    if lastEOL >= 0:
      stdout = stdout[0:lastEOL] 
    
    return stdout
  
  def _LogReturnCode(self, _rc, **args):
    if _rc > 0:
      self.Log('exit code: {0}'.format(_rc), **args)

