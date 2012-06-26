import sys
import stat
import os

from atta import Atta
from ..tasks.Base import Task
from ..tasks.Exec import Exec
from ..tools.Misc import LogLevel
from ..tools.Sets import FileSet
import atta.tools.OS as OS

class Javac(Task):
  '''
  .. snippet:: Javac
  
    .. code-block:: python

      Javac(srcs, destDir[, **tparams])}

    TODO: description

    :param srcs:             TODO
    :type srcs:              if string: file/dir/wildcard name or path (separator :) in which each item may be: file/dir/wildcard name
                             if list: each item may be: file/dir/wildcard name or FileSet
    :param string destDir:   TODO
    :param classPath:
    :param sourcePath:
    :param boolean debug:
    :param string debugLevel:
    :param javacParams:      TODO
    
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
      self.Log('\n*** Parameters:')
      self.LogIterable('srcs:', srcs)
      self.LogIterable('destDir:', [destDir])
      self.LogIterable('classPath:', classPath)
      self.LogIterable('sourcePath:', sourcePath)
      self.Log('debug: {0}'.format(debug))
      self.Log('debugLevel: {0}'.format(debugLevel))
      self.Log('')
      
    AddToPath = lambda path, name: path + os.path.normpath(name) + os.pathsep
    
    # prepare sourcepath
    sourcePathStr = ''
    for path in sourcePath:
      if len(path) > 0:
        #sourcePathStr = sourcePathStr + os.path.realpath(path) + os.pathsep
        sourcePathStr = AddToPath(sourcePathStr, path)
    
    # prepare user classpath
    classPathStr = ''
    for path in classPath:
      if len(path) > 0:
        #classPathStr = classPathStr + os.path.realpath(path) + os.pathsep
        classPathStr = AddToPath(classPathStr, path)

    RequiresCompile = lambda root, name: self.RequiresCompile(destDir, root, name, **tparams) 
            
    # collect source files
    srcsSet = FileSet(createEmpty = True)
    for src in srcs:
      if len(src) <= 0:
        continue
      
      if isinstance(src, FileSet):
        rootDir = src.rootDir
        sourcePathStr = AddToPath(sourcePathStr, rootDir)
        srcsSet.extend(src)
      else:
        if OS.Path.HasWildcards(src):
          rootDir, includes = OS.Path.Split(src)
          #sourcePathStr = sourcePathStr + os.path.realpath(rootDir) + os.pathsep
          sourcePathStr = AddToPath(sourcePathStr, rootDir) 
          srcsSet.AddFiles(rootDir, includes = includes, 
                           filter = RequiresCompile, realPaths = False, withRootDir = True)
        else:
          if os.path.isdir(src):
            #sourcePathStr = sourcePathStr + os.path.realpath(src) + os.pathsep
            sourcePathStr = AddToPath(sourcePathStr, src)
            srcsSet.AddFiles(src, includes = '**/*' + Javac.SourceExt(**tparams), 
                             filter = RequiresCompile, realPaths = False, withRootDir = True)
          else:
            #src = os.path.realpath(src)
            src = os.path.normpath(src)
            if os.path.exists(src):
              #sourcePathStr = sourcePathStr + os.path.split(src)[0] + os.pathsep
              rootDir = os.path.split(src)[0]
              sourcePathStr = AddToPath(sourcePathStr, rootDir)
              if RequiresCompile(rootDir, src):
                srcsSet += [src]
    
    if len(srcsSet) <= 0:
      self.Log('Nothing to compile in: {0}'.format(' '.join(srcs)), level = LogLevel.VERBOSE)
      self.returnCode = -1
      return None
    
    self.Log('Compiling %d source file(s) to: %s' % (len(srcsSet), destDir))
    self.LogIterable(None, srcsSet, level = LogLevel.VERBOSE)
    
    # prepare command line for java compiler
    params = tparams.get('javacParams', [])
    params.extend(['-d', destDir])
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
    self.InvokeJavac(params, **tparams)

  def RequiresCompile(self, destDir, srcDir, fileName, **tparams): 
    '''TODO: description'''
    dest = os.path.join(destDir, OS.Path.RemoveExt(fileName) + Javac.OutputExt(**tparams)) 
    src = os.path.join(srcDir, fileName)
    if not os.path.exists(dest):
      return True
    destTime = os.path.getmtime(dest)
    srcTime = os.path.getmtime(src)
    if srcTime > destTime:
      return True
    return False

  def InvokeJavac(self, params, **tparams):
    '''TODO: description'''
    e = Exec(Javac.Executable(**tparams), params, **tparams)
    self.returnCode = e.returnCode
    self.output = e.output
    
  @staticmethod
  def Executable(**tparams):
    '''TODO: description'''
    return 'javac'

  @staticmethod
  def SourceExt(**tparams):
    '''TODO: description'''
    return '.java'

  @staticmethod
  def OutputExt(**tparams):
    '''TODO: description'''
    return '.class'

    