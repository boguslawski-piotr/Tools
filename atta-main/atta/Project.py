import sys
import os
from datetime import datetime

# Python 2.7+
#import importlib

import atta
from tools.OS import *
from Log import *
from Env import *

class Project:
  '''
  Project class
    
  TODO: description
  '''
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
    prevDir = None
    moduleName = None
    module = None

    try: #{
      orgFileName = fileName
      fileName    = RemoveExt(os.path.normpath(os.path.realpath(fileName)))
      dirName     = os.path.dirname(fileName)
      moduleName  = os.path.basename(fileName)
      fileName    = fileName + '.py'
      if not os.path.exists(fileName):
        raise IOError(os.errno.ENOENT, 'File: {0} does not exists!'.format(fileName))
      
      logLevel = LogLevel.DEBUG
      Log('\n+++\nProject.Import(' + orgFileName + ')', level = logLevel)
      Log('  dirName = ' + dirName, level = logLevel)
      Log('  fileName = ' + dirName, level = logLevel)
      
      fullModuleName = moduleName
      if fileName[0:len(self.dirName)] == self.dirName:
        fullModuleName = RemoveExt(fileName.replace(self.dirName, '').replace(os.path.sep, '.'))
        fullModuleName = fullModuleName[(1 if fullModuleName[0] == '.' else 0):]
      else:
        fullModuleName = RemoveExt(orgFileName).replace('\\', '.').replace('/', '.')
      
      packageFileName = None
      if sys.modules.has_key(moduleName): #{
        lastDOT = fullModuleName.rfind('.')
        if lastDOT >= 0:
          lastDOT = fullModuleName.rfind('.', 0, lastDOT - 1)
          moduleName = fullModuleName[lastDOT + 1:]
        packageFileName = os.path.join(dirName, '__init__.py')
        if not os.path.exists(packageFileName):
          try: open(packageFileName, 'w').close()
          except: pass
        else:
          packageFileName = None
      #}
            
      prevDir = self.env.chdir(dirName)
      atta.file = BuildFile(fileName)
      
      try: #{
        Log('  fullModuleName = ' + fullModuleName, level = logLevel)
        Log('  moduleName = ' + moduleName, level = logLevel)
        Log('---\n', level = logLevel)
        
        sys.path.insert(0, dirName)
        # Python 2.7+
        #module = importlib.import_module(moduleName)
        # Python 2.3+
        __import__(moduleName)
        module = sys.modules[moduleName]
        
        if fullModuleName != moduleName \
           and not sys.modules.has_key(fullModuleName):
          sys.modules[fullModuleName] = module
        
        if packageFileName is not None:
          Remove(packageFileName)
          Remove(packageFileName + 'c')
          Remove(packageFileName + 'o')
      #}    
      except:
        raise
      finally:
        if prevDir is not None:
          self.env.chdir(prevDir)
    #}  
    except:
      raise
    finally:
      atta.file = prevAttaFile
    
    return (moduleName, module)

  def RunTarget(self, targetClass):
    targetClass = self._GetTargetClass(targetClass)
    if not self.executedTargets.has_key(targetClass):
      self.executedTargets[targetClass] = targetClass()
      for dependClass in self.executedTargets[targetClass].DependsOn:
        self.RunTarget(self._GetTargetClass(dependClass))
      self.executedTargets[targetClass]._Run()
    return
  
  def RunProject(self, environ, fileName, targets = ''):
    project = Project(self)
    if environ is None:
      environ = self.env.vars
    project._Run(environ, fileName, targets)
  
  '''private section'''
  
  def _Run(self, environ, buildFileName, targets):
    prevDir = os.getcwd()
    prevAttaProject = atta.project

    try: #{
      self.startTime = datetime.now()
      
      atta.project = self
      
      self.dirName = os.path.normpath(os.path.realpath(os.path.dirname(buildFileName)))
      self.fileName = os.path.join(self.dirName, RemoveExt(os.path.basename(buildFileName)) + '.py')
      self.env = Env(environ)
      self.env.chdir(self.dirName)

      if not os.path.exists(self.fileName):
        raise IOError(os.errno.ENOENT, 'Buildfile: {0} does not exists!'.format(self.fileName))
      
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
        self.executedTargets = {} # Behavior compatible with Ant.
        self.RunTarget(moduleName + '.' + targetName)
    
      self._End(Project.SUCCESSFUL)
    #}  
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
      targetClass = sys.modules[targetPackage].__dict__[Ext(targetClass)]
    return targetClass
    
  def _Dump(self):
    Log('*** Project', level = LogLevel.DEBUG)
    Log('Project.dirName = ' + self.dirName, level = LogLevel.DEBUG)
    Log('Project.fileName = ' + self.fileName, level = LogLevel.DEBUG)
    Log('Project.defaultTarget = ' + self.defaultTarget, level = LogLevel.DEBUG)
    Log('***', level = LogLevel.DEBUG)

