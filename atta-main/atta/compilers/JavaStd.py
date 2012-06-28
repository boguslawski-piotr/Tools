from atta import Atta
from Interfaces import IJavaCompiler
from ..tasks.Base import Task
from ..tasks.Exec import Exec
from ..tools.Misc import LogLevel

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
      
    .. snippetref:: ExecCommonParams2
     
    '''
    # prepare command line for java compiler
    params = tparams.get('javacParams', [])
    params.extend(['-d', destDir])
    debug = tparams.get('debug', False)
    debugLevel = tparams.get('debugLevel', None)
    if not debug: 
      params.append('-g:none')
    else:
      if debugLevel is None:
        params.append('-g')
      else:
        params.append('-g:' + debugLevel)
    classPath = tparams.get('classPath', '')
    if len(classPath) > 0:  
      params.extend(['-classpath', classPath])
    sourcePath = tparams.get('sourcePath', '')
    if len(sourcePath) > 0: 
      params.extend(['-sourcepath', sourcePath])
    params.extend(srcFiles)
    #'-verbose'

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
    #print os.environ['JAVA_HOME']
    return 'javac'
  
