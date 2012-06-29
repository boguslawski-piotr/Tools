import os
from atta import Atta, GetProject
from Interfaces import IJavaCompiler
from ..tasks.Base import Task
from ..tasks.Exec import Exec
from ..tools.Misc import LogLevel, isiterable
import atta.tools.OS as OS

class JavaStdCompiler(IJavaCompiler, Task):
  '''TODO: description'''
  def SourceExts(self, **tparams):
    return ['.java', '.aidl']

  def OutputExt(self, **tparams):
    return '.class'
  
  def Compile(self, srcFiles, destDir, **tparams):
    '''
    TODO: description
    
    .. snippet:: JavaStdCompilerParams
    
      :param boolean debug:
      :param string debugLevel:
      :param cParams:        The parameters passed directly to the compiler |None|.
      :type cParams:         string or list of strings
      
    .. snippetref:: ExecCommonParams2
     
    '''
    # prepare command line for java compiler
    params = tparams.get('cParams', [])
    if isinstance(params, basestring):
      params = params.split(' ')
      
    debug = tparams.get('debug', False)
    debugLevel = tparams.get('debugLevel', None)
    if not debug: 
      params.append('-g:none')
    else:
      if debugLevel is None:
        params.append('-g')
      else:
        params.append('-g:' + debugLevel)
        
    classPath = OS.Path.FromList(tparams.get('classPath', ''))
    if len(classPath) > 0:  
      params.extend(['-classpath', classPath])

    sourcePath = OS.Path.FromList(tparams.get('sourcePath', ''))
    if len(sourcePath) > 0: 
      params.extend(['-sourcepath', sourcePath])
    
    params.extend(['-d', destDir])
    params.extend(srcFiles)

    if Atta.logger.GetLevel() == LogLevel.DEBUG:
      self.LogIterable('\n*** Parameters:', params)
      self.Log('')
    
    # TODO: robic plik z params i przekazywac plik do javac (bo na linie komend to moze byc za duzo)
    
    # compile
    e = Exec(self.GetExecutable(**tparams), params, **tparams)
    self.returnCode = e.returnCode
    self.output = e.output
    return self.returnCode
  
  def GetOutput(self):
    return self.output

  def GetExecutable(self, **tparams):
    '''TODO: description'''
    javaHome = GetProject().env.get('JAVA_HOME')
    if javaHome is not None:
      return os.path.normpath(os.path.join(javaHome, 'bin/javac'))
    return 'javac'
  
