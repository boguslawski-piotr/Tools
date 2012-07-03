import sys
import os
import platform
import collections
from datetime import datetime, timedelta

# Python 2.7+
#import importlib

from tools.Misc import LogLevel
import tools.OS as OS
from Env import *
import Dependencies
import Deploy
import atta
import Dict

class Project:
  '''
  Project class
    
  TODO: description
  '''
  SUCCESSFUL = 0
  FAILED = 1

  def __init__(self, parent = None):
    self.name = ''
    '''TODO: description'''

    self.displayName = ''
    '''TODO: description'''

    self.description = ''
    '''TODO: description'''

    self.version = ''
    '''TODO: description'''

    self.url = ''
    '''TODO: description'''

    self.dirName = ''
    '''TODO: description'''
    
    self.fileName = ''
    '''TODO: description'''

    self.env = None
    '''TODO: description'''
    
    self.dependsOn = []
    '''TODO: description'''

    self.deployTo = []
    '''TODO: description'''
    
    self.defaultTarget = ''
    '''TODO: description'''

    self.targetsMap = {}
    '''TODO: description'''
    
    self._executedTargets = collections.OrderedDict()
    self._targetsLevel = 0
    self._parent = parent
    
  def Import(self, fileName):
    '''TODO: description'''
    moduleName = None
    module = None
    try: #{
      orgFileName = fileName
      fileName    = OS.Path.RemoveExt(os.path.normpath(os.path.realpath(fileName)))
      dirName     = os.path.dirname(fileName)
      moduleName  = os.path.basename(fileName)
      fileName    = fileName + '.py'
      if not os.path.exists(fileName):
        raise IOError(os.errno.ENOENT, 'File: {0} does not exists!'.format(fileName))
      
      logLevel = LogLevel.DEBUG
      Atta.logger.Log('\n+++\nProject.Import(' + orgFileName + ')', level = logLevel)
      Atta.logger.Log('  dirName = ' + dirName, level = logLevel)
      Atta.logger.Log('  fileName = ' + fileName, level = logLevel)
      
      fullModuleName = moduleName
      if fileName[0:len(self.dirName)] == self.dirName:
        fullModuleName = OS.Path.RemoveExt(fileName.replace(self.dirName, '').replace(os.path.sep, '.'))
        fullModuleName = fullModuleName[(1 if fullModuleName[0] == '.' else 0):]
      else:
        fullModuleName = OS.Path.RemoveExt(orgFileName).replace('\\', '.').replace('/', '.')
      
      packageFileName = None
      if sys.modules.has_key(moduleName):
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
              
      prevDir = self.env.chdir(dirName)
      atta.File._Set(fileName)
      try: #{
        Atta.logger.Log('  fullModuleName = ' + fullModuleName, level = logLevel)
        Atta.logger.Log('  moduleName = ' + moduleName, level = logLevel)
        Atta.logger.Log('---\n', level = logLevel)
        
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
          OS.RemoveFile(packageFileName)
          OS.RemoveFile(packageFileName + 'c')
          OS.RemoveFile(packageFileName + 'o')
      #}    
      except:
        raise
      finally:
        atta.File._Unset()
        if prevDir is not None:
          self.env.chdir(prevDir)
    #}  
    except:
      raise
    
    return (moduleName, module)

  def ResolveDependencies(self, data = None, scope = Dict.Scopes.compile, returnPackages = True):
    '''TODO: description'''
    resolver = Dependencies.Resolver()
    if resolver.Resolve(self.dependsOn if data is None else data, scope):
      return resolver.Result() if not returnPackages else (resolver.Result(), resolver.ResultPackages())
    else:
      return None if not returnPackages else (None, None)
  
  def GetTarget(self, targetClass):
    '''TODO: description'''
    targetClass = self._GetTargetClass(targetClass)
    target = targetClass()
    return target
  
  def RunTarget(self, targetClass):
    '''TODO: description'''
    targetClass = self._GetTargetClass(targetClass)
    if not self._executedTargets.has_key(targetClass):
      target = targetClass()
      if target.CanRun():
        self._targetsLevel += 1
        self._executedTargets[targetClass] = [target, self._targetsLevel]
        for dependClass in target.dependsOn:
          self.RunTarget(dependClass)
        target._Run()
        self._targetsLevel -= 1
      return target
    return None
  
  def RunProject(self, environ, fileName, targets = []):
    '''TODO: description'''
    project = Project(self)
    if environ is None:
      environ = self.env
    project._Run(environ, fileName, targets)
    return project
  
  def Deploy(self, packageId, files, baseDirName, data = None):
    deployer = Deploy.Deployer()
    return deployer.Deploy(packageId, files, baseDirName, self.deployTo if data is None else data)

  '''private section'''
  
  def _Run(self, environ, fileName, targets = []):
    prevDir = os.getcwd()
    prevAttaProject = atta.Project
    try:
      self.startTime = datetime.now()
      
      atta.Project = self
      
      self.dirName = os.path.normpath(os.path.realpath(os.path.dirname(fileName)))
      self.fileName = os.path.join(self.dirName, OS.Path.RemoveExt(os.path.basename(fileName)) + '.py')
      self.env = Env(environ)
      self.env.chdir(self.dirName)

      if not os.path.exists(self.fileName):
        raise IOError(os.errno.ENOENT, 'File: {0} does not exists!'.format(self.fileName))
      
      if self._parent is None:
        Atta.logger.Log('Buildfile: ' + self.fileName)
      
      moduleName, module = self.Import(self.fileName)
      
      if len(targets) <= 0 or len(targets[0]) <= 0:
        targets = [self.defaultTarget]
        if len(targets[0]) <= 0:
          Atta.logger.Log('You did not specify any target.',
                project = self.fileName,
                log = True)
          self._End(Project.SUCCESSFUL);
          return
      
      self.env._Dump()
      self._Dump()
      
      Atta.logger.Log(
            project = self.fileName,
            start = True,
            at = self.startTime)
      
      for targetName in targets:
        self._executedTargets.clear() # Behavior compatible with Ant.
        self._targetsLevel = 0
        self.RunTarget(moduleName + '.' + targetName)
        self._DumpExecutedTargets()
        
      self._End(Project.SUCCESSFUL)

    except Exception, e:
      self._End(Project.FAILED, e)
      raise

    finally:
      atta.Project = prevAttaProject
      self.env.chdir(prevDir)
      
  def _End(self, status, exception = None):
    self.endTime = datetime.now();
    if self._parent is None:
      Atta.logger.Log(
            project = self.fileName,
            end = True,
            status = ('SUCCESSFUL' if status == Project.SUCCESSFUL else 'FAILED!'),
            at = self.endTime,
            time = self.endTime - self.startTime,
            exception = exception,
            level = LogLevel.ERROR)
    return
  
  def _GetTargetClass(self, targetClass):
    def _SplitClass(name):
      return (OS.Path.RemoveExt(targetClass), OS.Path.Ext(targetClass, False))
    
    if isinstance(targetClass, basestring):
      tryTargetInProject = True
      while True:
        try:
          targetPackage, targetClassName = _SplitClass(targetClass)
          targetClass = sys.modules[targetPackage].__dict__[targetClassName]
        except Exception, e:
          firstDot = targetPackage.find('.')
          if firstDot >= 0:
            targetPackage = targetPackage[firstDot + 1:]
          else:
            key = None
            if len(targetClassName) > 0:
              key = targetClassName  
            else:
              # Coming here we have only one component of the target, without the module name.
              if tryTargetInProject:
                # Only once we check whether the target is in the main project file.
                # This allows to change the default behavior of targets collections 
                # that come with of Atta (such as Java or Android).
                targetClass = OS.Path.RemoveExt(os.path.basename(self.fileName)) + '.' + targetPackage
                tryTargetInProject = False
              else:
                key = targetPackage  
            if key is not None:
              if self.targetsMap.has_key(key):
                targetClass = self.targetsMap[key]
              else:
                raise AttaError(self, 'Can not find the %s.%s target.' % (targetPackage, targetClassName))
        else:
          break
    return targetClass
    
  def _Dump(self):
    Atta.logger.Log('*** Project', level = LogLevel.DEBUG)
    Atta.logger.Log('Project.dirName = ' + self.dirName, level = LogLevel.DEBUG)
    Atta.logger.Log('Project.fileName = ' + self.fileName, level = LogLevel.DEBUG)
    Atta.logger.Log('Project.defaultTarget = ' + self.defaultTarget, level = LogLevel.DEBUG)
    Atta.logger.Log('***', level = LogLevel.DEBUG)

  def _DumpExecutedTargets(self):
    Atta.logger.Log('\n*** Project {0}'.format(self.fileName), level = LogLevel.DEBUG)
    Atta.logger.Log('Project._executedTargets:', level = LogLevel.DEBUG)
    for i in self._executedTargets.values():
      Atta.logger.Log(('{0:>%d}{1}' % (i[1]*2)).format(' ', i[0].__class__), level = LogLevel.DEBUG)
    Atta.logger.Log('***', level = LogLevel.DEBUG)
