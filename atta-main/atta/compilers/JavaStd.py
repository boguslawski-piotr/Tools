'''.. Java related: TODO'''
import os

from ..tasks.Base import Task
from ..tasks.Exec import Exec
from ..tools.Misc import LogLevel
from ..tools import OS
from .. import Dict
from .. import GetProject
from .Interfaces import IJavaCompiler

class JavaStdCompiler(IJavaCompiler, Task):
  '''TODO: description'''
  def SourceExts(self, **tparams):
    return ['.java', '.aidl']

  def OutputExt(self, **tparams):
    return '.class'

  def Compile(self, srcFiles, destDir, **tparams):
    '''
    TODO: description
    
    Parameters:
    
    * **srcFiles** TODO
    * **destDir** (string)
    * **debug**
    * **debugLevel** (stirng)
    * **cParams**    The parameters passed directly to the compiler. (string or list of strings) |None|
      
    Common parameters from :py:class:`.Exec` task are also available.
    
    Returns exit code returned by executed ``javac`` command. 
    the same data as :py:class:`.Exec` task.
     
    '''
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

    params.extend(['-d', os.path.normpath(destDir)])

    params.extend(OS.Path.AsList(srcFiles))

    if self.LogLevel() == LogLevel.DEBUG:
      self.LogIterable(Dict.msgDumpParameters, params)
      self.Log('')

    # TODO: robic plik z params i przekazywac plik do javac (bo na linie komend to moze byc za duzo)

    # Compile.
    e = Exec(self.GetExecutable(**tparams), params, **tparams)
    self.returnCode = e.returnCode
    self.output = e.output
    return self.returnCode

  def GetOutput(self):
    return self.output

  def GetExecutable(self, **tparams):
    '''TODO: description'''
    javaHome = GetProject().env.get(Dict.JAVA_HOME)
    if javaHome is not None:
      return os.path.normpath(os.path.join(javaHome, Dict.JAVAC_EXE_IN_JAVA_HOME))
    return Dict.JAVAC_EXE

