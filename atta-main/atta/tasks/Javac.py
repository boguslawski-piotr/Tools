import sys
import stat
import os

from atta import Atta
from ..tasks.Base import Task
from ..tasks.Exec import Exec
from ..tools.Misc import LogLevel
from ..tools.Sets import FileSet
import atta.tools.OS as OS

def JavacExecutable(**tparams):
  return 'javac'

class Javac(Task):
  '''
  .. snippet:: Javac
  
    .. code-block:: python

      Javac(srcs, destDir[, **tparams])}

    TODO: description

    :param srcs:           TODO
    :type srcs:            string, string path or list of strings
    :param string destDir: TODO
    
  .. snippetref:: ExecCommonParams2
  .. snippetref:: ExecReturns

  .. snippet:: JavacUseCases
  
    Use cases:
    
    .. literalinclude:: ../../../tests/test_Java.py
  
  ''' 
  def __init__(self, srcs, destDir = '.', **tparams):
    # get parameters
    if isinstance(srcs, basestring):
      srcs = srcs.split(':')
    classPath = tparams.get('classPath', [])
    if isinstance(classPath, basestring):
      classPath = classPath.split(':')
    sourcePath = tparams.get('sourcePath', [])
    if isinstance(sourcePath, basestring):
      sourcePath = sourcePath.split(':')
    debug = tparams.get('debug', False)
    debugLevel = tparams.get('debugLevel', None)
    
    if Atta.logger.GetLevel() == LogLevel.DEBUG:
      self.Log('Parameters:')
      self.LogIterable('srcs:', srcs)
      self.LogIterable('destDir:', [destDir])
      self.LogIterable('classPath:', classPath)
      self.LogIterable('sourcePath:', sourcePath)
      self.Log('debug: {0}'.format(debug))
      self.Log('debugLevel: {0}'.format(debugLevel))
      self.Log('')
      
    # prepare destination directory
    destDir = os.path.realpath(destDir)
    
    # prepare sourcepath
    sourcePathStr = ''
    for path in sourcePath:
      if len(path) > 0:
        sourcePathStr = sourcePathStr + os.path.realpath(path) + os.pathsep
    
    # prepare user classpath
    classPathStr = ''
    for path in classPath:
      if len(path) > 0:
        classPathStr = classPathStr + os.path.realpath(path) + os.pathsep
        
    # collect source files
    srcsSet = FileSet(createEmpty = True)
    for src in srcs:
      if len(src) <= 0:
        continue
      if OS.Path.HasWildcards(src):
        rootDir, includes = OS.Path.Split(src)
        sourcePathStr = sourcePathStr + os.path.realpath(rootDir) + os.pathsep
        srcsSet.AddFiles(rootDir, includes = includes)
      else:
        if os.path.isdir(src):
          sourcePathStr = sourcePathStr + os.path.realpath(src) + os.pathsep
          srcsSet.AddFiles(src, includes = '**/*.java')
        else:
          src = os.path.realpath(src)
          if os.path.exists(src):
            sourcePathStr = sourcePathStr + os.path.split(src)[0] + os.pathsep
            srcsSet += [src]
    
    # check what files need to be compiled
    # TODO:
    #print sourcePath
    #print destDir
        
    if len(srcsSet) <= 0:
      self.Log('Nothing to compile in: {0}'.format(' '.join(srcs)))
      return None
    
    self.Log('Compiling %d source file(s) to: %s' % (len(srcsSet), destDir))
    self.LogIterable(None, srcsSet, level = LogLevel.VERBOSE)
    
    # prepare command line for java compiler
    params = ['-d', destDir]
    if not debug: 
      params.append('-g:none')
    else:
      if debugLevel is None:
        params.append('-g')
      else:
        params.append('-g:' + debugLevel)
    if len(classPathStr) > 0:  
      params.extend(['-classpath', classPathStr])
    if len(sourcePathStr) > 0: 
      params.extend(['-sourcepath', sourcePathStr])
    params.extend(srcsSet)
    #'-verbose'

    if Atta.logger.GetLevel() == LogLevel.DEBUG:
      self.Log('')
      self.LogIterable('Parameters for java compiler:', params)
      self.Log('')
    
    # compile
    e = Exec(JavacExecutable(**tparams), params, **tparams)
    self.re = e.returnCode
    self.output = e.output
    