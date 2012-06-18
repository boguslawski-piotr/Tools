import sys
import os
import importlib
from datetime import datetime

from atta.OS import *
from atta.Log import *
from atta.Env import *
import atta

## Project class
#  TODO: description
class Project:
  SUCCESSFUL = 0
  FAILED = 1

  def __init__(self, parent = None):
    self.parent = parent
    
    self.name = ''
    self.description = ''
    
    self.dirName = ''
    self.fileName = ''
    self.env = None
    
    self.defaultTarget = ''
    self.executedTargets = {}
    
  def ParseScript(self, script):
    return script
  
  def Import(self, fileName):
    class BuildFile:
      def __init__(self, fileName):
        self.name = fileName
    
    prevAttaFile = atta.file
    moduleName = None
    _file = None

    try:
      fileName   = RemoveExt(os.path.normpath(os.path.realpath(fileName)))
      dirName    = os.path.dirname(fileName)
      moduleName = os.path.basename(fileName)
      fileName   = fileName + '.py'
      if not os.path.exists(fileName):
        raise IOError(os.errno.ENOENT, 'File: {0} does not exists!'.format(fileName))
      
      packageFileName = None
      
      if sys.modules.has_key(moduleName):
        moduleName = RemoveExt(fileName.replace(self.dirName, '').replace(os.path.sep, '.'))
        if moduleName[0] == '.': 
          moduleName = moduleName[1:]
          
        packageFileName = os.path.join(dirName, '__init__.py')
        if not os.path.exists(packageFileName):
          Remove(packageFileName)
          try: open(packageFileName, 'w').close()
          except: pass
        else:
          packageFileName = None
            
      atta.file = BuildFile(fileName)
      prevDir = self.env.chdir(dirName)
      try:
        sys.path.insert(0, dirName)
        _file = importlib.import_module(moduleName)
        if packageFileName is not None:
          Remove(packageFileName)
          
      except:
        raise
      finally:
        self.env.chdir(prevDir)
      
    except:
      raise
    finally:
      atta.file = prevAttaFile
    
    return (moduleName, _file)

  def RunTarget(self, targetClass):
    targetClass = self._GetTargetClass(targetClass)
    if not self.executedTargets.has_key(targetClass):
      self.executedTargets[targetClass] = targetClass()
      for dependClass in self.executedTargets[targetClass].DependsOn:
        self.RunTarget(self._GetTargetClass(dependClass))
      self.executedTargets[targetClass]._Run()
    return
  
  def RunProject(self, environ, buildFileName, targets = ''):
    project = Project(self)
    if environ is None:
      environ = self.env.vars
    project._Run(environ, buildFileName, targets)
  
  ## \privatesection
  
  def _Run(self, environ, buildFileName, targets):
    prevDir = os.getcwd()
    prevAttaProject = atta.project

    try:
      self.startTime = datetime.now()
      
      atta.project = self
      
      self.dirName = os.path.normpath(os.path.realpath(os.path.dirname(buildFileName)))
      self.fileName = os.path.join(self.dirName, RemoveExt(os.path.basename(buildFileName)) + '.py')
      if not os.path.exists(self.fileName):
        raise IOError(os.errno.ENOENT, 'Buildfile: {0} does not exists!'.format(self.fileName))
      
      self.env = Env(environ)
      self.env.chdir(self.dirName)
      
      if self.parent is None:
        Log('Buildfile: ' + self.fileName)
      
      moduleName, module = self.Import(self.fileName)
      
      if len(targets) <= 0 or len(targets[0]) <= 0:
        targets = [self.defaultTarget]
        if len(targets[0]) <= 0:
          self._End(Project.SUCCESSFUL);
          return
      
      self.env._Dump()
      self._Dump()
      
      LogNM(project = self.fileName,
            start = True,
            at = self.startTime)
      
      for targetName in targets:
        self.executedTargets = {}
        self.RunTarget(moduleName + '.' + targetName)
    
      self._End(Project.SUCCESSFUL)
      
    except Exception, e:
      self._End(Project.FAILED, e)
      raise
    
    finally:
      atta.project = prevAttaProject
      self.env.chdir(prevDir)
      
  def _End(self, status, exception = None):
    self.endTime = datetime.now();
    if self.parent is None:
      LogNM(project = self.fileName,
            end = True,
            status = ('SUCCESSFUL' if status == Project.SUCCESSFUL else 'FAILED!'),
            at = self.endTime,
            time = self.endTime - self.startTime,
            exception = exception,
            level = LogLevel.ERROR)
    return
  
  def _GetTargetClass(self, targetClass):
    if isinstance(targetClass, basestring):
      targetPackage = RemoveExt(targetClass)
      targetClass = Ext(targetClass)
      targetClass = sys.modules[targetPackage].__dict__[targetClass]
    return targetClass
    
  def _Dump(self):
    Log('Project.dirName = ' + self.dirName, level = LogLevel.DEBUG)
    Log('Project.fileName = ' + self.fileName, level = LogLevel.DEBUG)
    Log('Project.defaultTarget = ' + self.defaultTarget, level = LogLevel.DEBUG)

