'''.. Java related: TODO: java'''
import sys
import stat
import os

from atta import Atta
from ..tools.internal.Misc import ObjectFromClass
from ..tools.Strategies import SrcNewerStrategy
from ..compilers.JavaStd import JavaStdCompiler
from ..tasks.Base import Task
from ..tools.Misc import LogLevel
from ..tools.Sets import FileSet
import atta.tools.OS as OS
import atta.Dict as Dict
  
class Javac(Task):
  '''
    TODO: description
    
    Parameters:
  
    * **srcs**        TODO
      if string: file/dir/wildcard name or path (separator :) in which each item may be: file/dir/wildcard name
      if list: each item may be: file/dir/wildcard name or FileSet
    * **destDir**     TODO
    * **classPath**
    * **sourcePath**
    
    TODO Kiedy uzywany jest kompilator :py:class:`.JavaStdCompiler`...
    parameters ``debug``, ``debugLevel`` and ``cParams`` described in 
    :py:meth:`.JavaStdCompiler.Compile` are also available.
    Just as common parameters from :py:class:`.Exec` task.
    
    Returns object with two attributtes:
  
    * **returnCode** Exit code returned by :py:meth:`.IJavaCompiler.Compile`.
    * **output**     Data returned by :py:meth:`.ICompiler.GetOutput`.
    
    Advanced parameters:
    
    * **requiresCompileImpl**   Physical implementation of :py:meth:`RequiresCompile` method. 
      It must be class that implements :py:meth:`.ICompareStrategy.ActionNeeded`. 
  
    * **compilerImpl**          Implementation of wrapper to the Java compiler. 
      It must be class that implements :py:class:`.IJavaCompiler`.
  
    **Methods:**
  ''' 
  def __init__(self, srcs, destDir = '.', **tparams):
    self._DumpParams(locals())

    self._requiresCompileImpl = ObjectFromClass(tparams.get('requiresCompileImpl', Javac.GetDefaultRequiresCompileImpl()))
    self._compilerImpl = ObjectFromClass(tparams.get('compilerImpl', Javac.GetDefaultCompilerImpl()))
    
    srcs = OS.Path.AsList(srcs)
    classPath = OS.Path.AsList(tparams.get(Dict.paramClassPath, []))
    sourcePath = OS.Path.AsList(tparams.get(Dict.paramSourcePath, []))
    
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
      self.Log(Dict.msgNothingToCompile.format(' '.join(srcs)), level = LogLevel.VERBOSE)
      self.returnCode = -1
      return None
    
    self.Log(Dict.msgCompilingTo % (len(srcsSet), destDir))
    self.LogIterable(None, srcsSet, level = LogLevel.VERBOSE)
    
    tparams[Dict.paramSourcePath] = list(set(sourcePath))
    tparams[Dict.paramClassPath] = list(set(classPath))
    self.returnCode = self._compilerImpl.GetObject().Compile(srcsSet, destDir, **tparams)
    self.output = self._compilerImpl.GetObject().GetOutput()

  _defaultRequiresCompileImpl = ObjectFromClass(SrcNewerStrategy)
    
  @staticmethod
  def SetDefaultRequiresCompileImpl(_class):
    '''Sets default implementation of :py:meth:`RequiresCompile` method. 
       It may be any class that implements :py:meth:`.ICompareStrategy.ActionNeeded`'''
    Javac._defaultRequiresCompileImpl = ObjectFromClass(_class)

  @staticmethod
  def GetDefaultRequiresCompileImpl():
    return Javac._defaultRequiresCompileImpl.GetClass()
    
  def RequiresCompile(self, destDir, srcDir, fileName, **tparams): 
    '''TODO: description'''
    dest = os.path.join(destDir, OS.Path.RemoveExt(fileName) + self._compilerImpl.GetObject().OutputExt(**tparams)) 
    src = os.path.join(srcDir, fileName)
    return self._requiresCompileImpl.GetObject().ActionNeeded(src, dest)

  _defaultCompilerImpl = ObjectFromClass(JavaStdCompiler) 

  @staticmethod
  def SetDefaultCompilerImpl(_class):
    '''Sets default Java compiler. 
       It may be any class that implements :py:class:`.IJavaCompiler`'''
    Javac._defaultCompilerImpl = ObjectFromClass(_class)

  @staticmethod
  def GetDefaultCompilerImpl():
    return Javac._defaultCompilerImpl.GetClass()

