'''TODO: description'''
import sys
import os
import types
from datetime import datetime

# Python 2.7+
#import importlib

from .tools.Misc import LogLevel
from .tools import OS
from .tools import Ver
from .Env import Env
from . import Dependencies, Deploy, Dict
from . import AttaError, Atta, File, GetProject, _SetProject

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

    self.version = None
    '''TODO: description'''

    self.url = ''
    '''TODO: description'''

    self.dirName = ''
    '''TODO: description'''

    self.fileName = ''
    '''TODO: description'''

    self.env = None
    '''TODO: description'''

    self.dvcs = None
    '''object from class implements dvcs.IDvcs TODO: description'''

    self.dependsOn = []
    '''TODO: description'''

    self.deployTo = []
    '''TODO: description'''

    self.defaultTarget = ''
    '''TODO: description'''

    self.targets = []
    '''List of targets passed to Atta in the command line or 
       in the parameters of the method :py:meth:`.Project.RunProject`.'''

    self.targetsMap = {}
    '''TODO: description'''

    self._executedTargets = {} #collections.OrderedDict()
    self._executedTargetsList = []
    self._targetsLevel = 0
    self._parent = parent

  def Import(self, fileName):
    '''TODO: description'''
    moduleName = None
    module = None
    try:
      orgFileName = fileName
      fileName = OS.Path.RemoveExt(os.path.normpath(os.path.realpath(fileName)))
      dirName = os.path.dirname(fileName)
      moduleName = os.path.basename(fileName)
      fileName = fileName + '.py'
      if not os.path.exists(fileName):
        raise IOError(os.errno.ENOENT, Dict.errFileNotExists % fileName)

      logLevel = LogLevel.DEBUG
      Atta.Log('\n+++\nProject.Import(' + orgFileName + ')', level = logLevel)
      Atta.Log('  dirName = ' + dirName, level = logLevel)
      Atta.Log('  fileName = ' + fileName, level = logLevel)

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
      File._Set(fileName)
      try:
        Atta.Log('  fullModuleName = ' + fullModuleName, level = logLevel)
        Atta.Log('  moduleName = ' + moduleName, level = logLevel)
        Atta.Log('---\n', level = logLevel)

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

      except:
        raise
      finally:
        File._Unset()
        if prevDir is not None:
          self.env.chdir(prevDir)

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
    if types.FunctionType == type(targetClass):
      return targetClass
    target = targetClass()
    return target

  def RunTarget(self, targetClass, force = False):
    '''TODO: description'''
    targetClass = self._GetTargetClass(targetClass)
    if force or not self._executedTargets.has_key(targetClass):
      if types.FunctionType == type(targetClass):
        # Target is a normal function.
        self._executedTargetsList.append([targetClass, self._targetsLevel])
        self._targetsLevel += 1
        self._executedTargets[targetClass] = targetClass
        if Dict.dependsOn in dir(targetClass):
          for dependClass in targetClass.dependsOn:
            self.RunTarget(dependClass)
        Atta.Log(start = True, target = targetClass.__name__)
        targetClass()
        Atta.Log(end = True, target = targetClass.__name__)
        self._targetsLevel -= 1
      else:
        # Target is a class (and we assume that iherits from atta.targets.Base.Target)
        target = targetClass()
        if target.CanRun():
          self._executedTargetsList.append([target, self._targetsLevel])
          self._targetsLevel += 1
          if target._RunPrepare():
            self._executedTargets[targetClass] = target
            for dependClass in target.dependsOn:
              self.RunTarget(dependClass)
            target._Run()
            target._RunFinalize()
          self._targetsLevel -= 1
        return target
    return None

  def RunProject(self, environ, fileName, targets = None):
    '''TODO: description'''
    project = Project(self)
    if environ is None:
      environ = self.env
    project._Run(environ, fileName, (targets if targets else []))
    return project

  def Deploy(self, packageId, files, baseDirName, data = None):
    '''TODO: description'''
    deployer = Deploy.Deployer()
    return deployer.Deploy(packageId, files, baseDirName, self.deployTo if data is None else data)

  '''private section'''

  def _Run(self, environ, fileName, targets):
    prevDir = os.getcwd()
    prevAttaProject = GetProject()
    try:
      self.startTime = datetime.now()

      #atta.Project = self
      _SetProject(self)

      if os.path.isdir(fileName):
        fileName = os.path.join(fileName, Dict.defaultBuildFileName)
      self.dirName = os.path.normpath(os.path.realpath(os.path.dirname(fileName)))
      self.fileName = os.path.join(self.dirName, OS.Path.RemoveExt(os.path.basename(fileName)) + '.py')
      if not os.path.exists(self.fileName):
        raise IOError(os.errno.ENOENT, Dict.errFileNotExists % self.fileName)

      self.env = Env(environ)
      self.env.chdir(self.dirName)
      self.version = Ver.Version(createIfNotExists = False)
      self.targets = targets

      if self._parent is None:
        Atta.Log('Buildfile: ' + self.fileName)

      moduleName, module = self.Import(self.fileName)

      if len(targets) <= 0 or len(targets[0]) <= 0:
        targets = [self.defaultTarget]
        if len(targets[0]) <= 0:
          Atta.Log('You did not specify any target.',
                project = self.fileName,
                log = True)
          self._End(Project.SUCCESSFUL);
          return

      self.env._Dump()
      self._Dump()

      Atta.Log(
            project = self.fileName,
            start = True,
            at = self.startTime)

      if self.version != None:
        self.version._CreateIfNotExists()

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
      #atta.Project = prevAttaProject
      _SetProject(prevAttaProject)
      if self.env:
        self.env.chdir(prevDir)

  def _End(self, status, exception = None):
    self.endTime = datetime.now();
    if self._parent is None:
      Atta.Log(
            project = self.fileName,
            end = True,
            status = ('SUCCESSFUL' if status == Project.SUCCESSFUL else 'FAILED!'),
            at = self.endTime,
            time = self.endTime - self.startTime,
            exception = exception,
            level = LogLevel.ERROR if status == Project.FAILED else LogLevel.INFO)
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
        except Exception as e:
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
    if Atta.LogLevel() == LogLevel.DEBUG:
      Atta.Log('*** Project')
      Atta.Log('Project.dirName = ' + self.dirName)
      Atta.Log('Project.fileName = ' + self.fileName)
      Atta.Log('Project.defaultTarget = ' + self.defaultTarget)
      Atta.Log('***')

  def _DumpExecutedTargets(self):
    if Atta.LogLevel() == LogLevel.DEBUG:
      Atta.Log('\n*** Project: {0}'.format(self.fileName))
      Atta.Log('executed targets:')
      et = self._executedTargetsList
      et.reverse()
      for i in et:
        Atta.Log('  ' + ' ' * i[1] * 2 + '{0}'.format(i[0].__class__))
      Atta.Log('***')
