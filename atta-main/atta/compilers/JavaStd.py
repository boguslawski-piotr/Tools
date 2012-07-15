""".. Java related: TODO"""
import os
import tempfile

from ..tasks.Base import Task
from ..tasks.Exec import Exec
from ..tools import OS
from .. import LogLevel
from .. import Dict
from .Interfaces import IJavaCompiler

class JavaStdCompiler(IJavaCompiler, Task):
  """TODO: description"""
  def SourceExts(self, **tparams):
    return ['.java', '.aidl']

  def OutputExt(self, **tparams):
    return '.class'

  def Compile(self, srcFileNames, destDirName, **tparams):
    """
    TODO: description

    Parameters:

    * **srcFiles** TODO
    * **destDirName** (string)
    * **debug**
    * **debugLevel** (stirng)
    * **cParams**    The parameters passed directly to the compiler. (string or list of strings) |None|

    Common parameters from :py:class:`.Exec` task are also available.

    Returns exit code returned by executed ``javac`` command.
    the same data as :py:class:`.Exec` task.

    """
    # Prepare command line for java compiler.
    params = OS.Path.AsList(tparams.get('cParams', []), ' ')

    debug = tparams.get('debug', False)
    debugLevel = tparams.get('debugLevel', None)
    if not debug:
      params.append('-g:none')
    else:
      if debugLevel is None:
        params.append('-g')
      else:
        params.append('-g:' + debugLevel)

    classPath = OS.Path.FromList(tparams.get(Dict.paramClassPath, ''))
    if len(classPath) > 0:
      params.extend(['-classpath', os.path.normpath(classPath)])

    sourcePath = OS.Path.FromList(tparams.get(Dict.paramSourcePath, ''))
    if len(sourcePath) > 0:
      params.extend(['-sourcepath', os.path.normpath(sourcePath)])

    params.extend(['-d', os.path.normpath(destDirName)])

    params.extend(OS.Path.AsList(srcFileNames))

    if self.LogLevel() == LogLevel.DEBUG:
      self.LogIterable(Dict.msgDumpParameters, params)
      self.Log('')

    # Create temporary file with all parametres for javac.
    argfile = tempfile.NamedTemporaryFile(delete = False)
    cparams = ['@' + argfile.name]
    for p in params:
      if p.startswith('-J'):
        cparams.append(p)
      else:
        argfile.write(p + '\n')
    argfile.close()

    # Compile.
    e = Exec(self.GetExecutable(**tparams), cparams, **tparams)
    self.returnCode = e.returnCode
    self.output = e.output

    OS.RemoveFile(argfile.name, True, False)
    return self.returnCode

  def GetExecutable(self, **tparams):
    """TODO: description"""
    JAVA_HOME = self.Env().get(Dict.JAVA_HOME)
    if JAVA_HOME:
      return os.path.normpath(os.path.join(JAVA_HOME, Dict.JAVAC_EXE_IN_JAVA_HOME))
    executable = self.Env().which(Dict.JAVAC_EXE_IN_PATH)
    return executable if executable else Dict.JAVAC_EXE
