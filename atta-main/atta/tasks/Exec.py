import io
import sys
import os
import subprocess
import threading

import atta 
#import project
from ..BaseClasses import Task
from ..Log import LogLevel

class Exec(Task):
  '''
  .. snippet:: Exec
  
    .. code-block:: python

      Exec(executable[, params, **tparams])}

    Executes a system command. 

  .. snippet:: ExecAdditionalInfo
  
    TODO: detailed information
    
  .. snippet:: ExecParams

    :param string executable:   The command to execute without any command line arguments.
    
  .. snippet:: ExecCommonParams

    :param params:              Command line arguments |None|.
    :type params:               list of strings
    :param boolean failOnError: Stop the buildprocess if the command exits with a return code signaling failure |True|.
    :param boolean logOutput:   TODO: Przesyla stdout and stderr do logu Atta |True|. 
    :param boolean useSheel:    Command will be executed through the shell |True|. 
                                More information can be found in `subprocess.Popen <http://docs.python.org/library/subprocess.html>`_ documentation.
    :param dict env:            Environment variables. Completely replace the variables from the project |None|.
                        
  .. snippet:: ExecReturns
                          
    :return: Object with two attributtes:
    
      - returnCode (int) - Exit code returned by executed command.
      - output (string)  - Captured contents of stdout and stderr.
 
  .. todo::

    - Add reading environment variables set by the executed process
    - Parameters: os and osFamily

  .. snippet:: ExecUseCases
  
    Use cases:
    
    .. literalinclude:: ../../../tests/test_exec.py
    .. literalinclude:: ../../../tests/test_env2.py

  '''
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

  '''private section'''
  
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

