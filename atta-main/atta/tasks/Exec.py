'''.. Execution: Executes a system command: exec'''
import io
import sys
import os
import subprocess
import threading

import atta 
import atta.Dict as Dict
import atta.tools.DefaultVarsExpander
import atta.tools.OS as OS
from ..tasks.Base import Task
from ..tools.Misc import LogLevel

class Exec(Task):
  '''
  Executes a system command. 

  TODO: detailed information
    
  Parameters:
  
  * **executable** - The command to execute without any command line arguments. |str|
  * **params** -     Command line arguments. (string or list of strings) |None| 
    
  General parameters available in many tasks that use internally ``Exec`` task:
  
  * **failOnError** - Stop the buildprocess if the command exits with a return code signaling failure. |bool| |True|
  * **logOutput** -   TODO: Przesyla stdout and stderr do logu Atta. |True| 
  * **useSheel** -    Command will be executed through the shell. 
    More information can be found in :py:class:`subprocess.Popen` documentation. |True|
  * **env** -         Environment variables. Completely replace the variables from the project |None|.
                        
  Exec returns object with two attributtes:
  
  * **returnCode** - Exit code returned by executed command.
  * **output** -     Captured contents of stdout and stderr.
 
  In ``executable`` parameter you can use special macros: 
  
    ``${bat}, ${cmd} or ${exe}`` on Windows will add ``.bat/.cmd/.exe`` to the `executable`, 
    on other systems will not add anything 
    
    ``${sh}`` on non Windows systems will add ``.sh``, on Windows will add ``.bat``.
      
  .. todo::

    - Add reading environment variables set by the executed process
    - Parameters: os and osFamily

  '''
  def __init__(self, executable, params = [], **tparams):  
    params = OS.Path.AsList(params, ' ')
    failOnError = tparams.get('failOnError', True)
    self.logOutput = tparams.get('logOutput', True)
    useShell = tparams.get('useShell', True)
    env = tparams.get('env', None)
    
    _output = ''
    _rc = 0
    
    shExt  = '.sh'  if not OS.IsWindows() else '.bat'
    batExt = '.bat' if OS.IsWindows() else ''
    cmdExt = '.cmd' if OS.IsWindows() else ''
    exeExt = '.exe' if OS.IsWindows() else ''
    executable = atta.tools.DefaultVarsExpander.Expander().Expand(executable, bat = batExt, cmd = cmdExt, exe = exeExt, sh = shExt)
    
    _params = [executable]
    _params.extend(params)
    if env is None:
      if atta.Project is None:
        env = os.environ
      else:
        env = atta.GetProject().env
    
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
      self.Log(Dict.msgExitCode.format(_rc), **args)

