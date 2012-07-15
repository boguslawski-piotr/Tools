'''.. Execution: Executes a system command: exec'''
import os
import subprocess
import threading

from ..tools import DefaultVarsExpander
from .. import Dict, OS, LogLevel, Task

class Exec(Task):
  '''
  Executes a system command.

  TODO: detailed information

  Parameters:

  * **executable** |req| -   The command to execute without any command line arguments.
  * **params** |None| -      Command line arguments. (string or list of strings)

  General parameters available in many tasks that use internally ``Exec`` task:

  * **failOnError** |True| - Stop the buildprocess if the command exits with a return code signaling failure.
  * **logOutput** |True| -   TODO: Przesyla stdout and stderr do logu Atta.
  * **useShell** |True| -    Command will be executed through the shell. More information can be found in :py:class:`subprocess.Popen` documentation.
  * **env** |None| -         Environment variables. Completely replace the variables from the project.
  * **dirName** `(.)` -      The directory in which the command should be executed.

  Exec returns object with two attributtes:

  * **returnCode** - Exit code returned by executed command.
  * **output** -     Captured contents of stdout and stderr.

  In **executable** parameter you can use special macros:

    ``${bat}, ${cmd} or ${exe}`` on Windows will add ``.bat/.cmd/.exe`` to the `executable`,
    on other systems will not add anything

    ``${sh}`` on non Windows systems will add ``.sh``, on Windows will add ``.bat``.

  .. todo::

    - Add reading environment variables set by the executed process
    - Parameters: os and osFamily

  '''
  def __init__(self, executable, params = None, **tparams):
    params = OS.Path.AsList(params, ' ')
    failOnError = tparams.get(Dict.paramFailOnError, True)
    self.logOutput = tparams.get(Dict.paramLogOutput, True)
    useShell = tparams.get('useShell', True)
    env = tparams.get('env', None)
    dirName = tparams.get(Dict.paramDirName, '.')

    shExt = '.sh'  if not OS.IsWindows() else '.bat'
    batExt = '.bat' if OS.IsWindows() else ''
    cmdExt = '.cmd' if OS.IsWindows() else ''
    exeExt = '.exe' if OS.IsWindows() else ''
    executable = DefaultVarsExpander.Expander().Expand(executable, bat = batExt, cmd = cmdExt, exe = exeExt, sh = shExt)

    _params = [executable]
    _params.extend(params)
    if env is None:
      env = self.Env()

    _output = ''
    _rc = 0

    ocwd = self.Env().chdir(dirName)
    try:
      process = subprocess.Popen(_params, stdout = subprocess.PIPE, stderr = subprocess.STDOUT,
                                 bufsize = 1, env = env, shell = useShell)
      _output = self._communicate(process)
      _rc = process.poll()
    finally:
      self.Env().chdir(ocwd)
    if _rc:
      if failOnError:
        if not self.logOutput: self.Log(_output, level = LogLevel.ERROR)
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
      stdout_thread = threading.Thread(target = self._reader,
                                       args = (process.stdout, stdout))
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
