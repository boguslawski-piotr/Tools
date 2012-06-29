import sys
import stat
import os

from atta import Atta
from ..tools.internal.Misc import ObjectFromClass
from ..Strategies import SrcNewerStrategy
from ..compilers.JavaStd import JavaStdCompiler
from ..tasks.Base import Task
from ..tools.Misc import LogLevel
from ..tools.Sets import FileSet
import atta.tools.OS as OS
  
class Javac(Task):
  '''
  .. code-block:: python

    Javac(srcs, destDir[, **tparams])}

  TODO: description

  .. snippetref:: ExecReturns

  :param srcs:             TODO
  :type srcs:              if string: file/dir/wildcard name or path (separator :) in which each item may be: file/dir/wildcard name
                           if list: each item may be: file/dir/wildcard name or FileSet
  :param string destDir:   TODO
  :param classPath:
  :param sourcePath:

  Standard java compiler:
  
  .. snippetref:: JavaStdCompilerParams

  A deeper look:
  
  :param requiresCompileImpl: Physical implementation of :py:meth:`RequiresCompile` method. 
  :type requiresCompileImpl:  class that implements :py:meth:`atta.Interfaces.ICompareStrategy.ActionNeeded` 
                              passed through an instance of :py:class:`atta.tools.internal.Misc.ObjectFromClass`
  :param compilerImpl:        Java compiler. 
  :type compilerImpl:         class that implements :py:class:`atta.compilers.Interfaces.IJavaCompiler`
                              passed through an instance of :py:class:`atta.tools.internal.Misc.ObjectFromClass`

  .. snippet:: JavacUseCases
  
    Use cases:
    
    .. literalinclude:: ../../../tests/test_Java.py
  
  ''' 
  def __init__(self, srcs, destDir = '.', **tparams):
    self._DumpParams(locals())

    self._requiresCompileImpl = tparams.get('requiresCompileImpl', Javac._defaultRequiresCompileImpl)
    self._compilerImpl = tparams.get('compilerImpl', Javac._defaultCompilerImpl)
    
    srcs = OS.Path.AsList(srcs)
    classPath = OS.Path.AsList(tparams.get('classPath', []))
    sourcePath = OS.Path.AsList(tparams.get('sourcePath', []))
    
    RequiresCompile = lambda root, name: self.RequiresCompile(destDir, root, name, **tparams) 
    
    # collect source files
    srcsSet = FileSet(createEmpty = True)
    for src in srcs:
      if len(src) <= 0:
        continue
      if isinstance(src, FileSet):
        rootDir = src.rootDir
        sourcePath.append(rootDir)
        srcsSet.extend(src)
      else:
        if OS.Path.HasWildcards(src):
          rootDir, includes = OS.Path.Split(src)
          if len(rootDir) <= 0:
            rootDir = '.'
          sourcePath.append(rootDir) 
          srcsSet.AddFiles(rootDir, includes = includes, 
                           filter = RequiresCompile, realPaths = False, withRootDir = True)
        else:
          if os.path.isdir(src):
            sourcePath.append(src)
            srcExts = self._compilerImpl.GetObject().SourceExts(**tparams)
            if isinstance(srcExts, basestring):
              srcExts = [srcExts]
            includes = []
            for srcExt in srcExts:
              includes.append('**/*' + srcExt)
            srcsSet.AddFiles(src, includes, 
                             filter = RequiresCompile, realPaths = False, withRootDir = True)
          else:
            src = os.path.normpath(src)
            if os.path.exists(src):
              rootDir = os.path.split(src)[0]
              if RequiresCompile(rootDir, src):
                sourcePath.append(rootDir)
                srcsSet += [src]
    
    if len(srcsSet) <= 0:
      self.Log('Nothing to compile in: {0}'.format(' '.join(srcs)), level = LogLevel.VERBOSE)
      self.returnCode = -1
      return None
    
    self.Log('Compiling %d source file(s) to: %s' % (len(srcsSet), destDir))
    self.LogIterable(None, srcsSet, level = LogLevel.VERBOSE)
    
    tparams['sourcePath'] = list(set(sourcePath))
    tparams['classPath'] = list(set(classPath))
    self.returnCode = self._compilerImpl.GetObject().Compile(srcsSet, destDir, **tparams)
    self.output = self._compilerImpl.GetObject().GetOutput()

  @staticmethod
  def SetDefaultRequiresCompileImpl(_class):
    '''Sets default implementation of :py:meth:`RequiresCompile` method. 
       It may be any class that implements :py:meth:`atta.Interfaces.ICompareStrategy.ActionNeeded`'''
    Javac._defaultRequiresCompileImpl = ObjectFromClass(_class)
  
  _defaultRequiresCompileImpl = ObjectFromClass(SrcNewerStrategy)
    
  def RequiresCompile(self, destDir, srcDir, fileName, **tparams): 
    '''TODO: description'''
    dest = os.path.join(destDir, OS.Path.RemoveExt(fileName) + self._compilerImpl.GetObject().OutputExt(**tparams)) 
    src = os.path.join(srcDir, fileName)
    return self._requiresCompileImpl.GetObject().ActionNeeded(src, dest)

  @staticmethod
  def SetDefaultCompilerImpl(_class):
    '''Sets default Java compiler. 
       It may be any class that implements :py:class:`atta.compilers.Interfaces.IJavaCompiler`'''
    Javac._defaultRequiresCompileImpl = ObjectFromClass(_class)

  _defaultCompilerImpl = ObjectFromClass(JavaStdCompiler) 
