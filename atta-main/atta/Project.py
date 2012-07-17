"""TODO: description"""
import sys
import os
import types
from datetime import datetime

from . import LogLevel, OS, Dict, Version, Env, PackageId
from . import AttaError, Atta, File, _GetProject, _SetProject

class Project:
  """
  Project class

  TODO: description
  """
  SUCCESSFUL = 0
  FAILED = 1

  def __init__(self, parent = None):
    #: DOCTODO: description
    self.groupId = ''

    #: DOCTODO: description; defaults to project directory name
    self.name = ''

    #: DOCTODO: description
    self.type = ''

    #: DOCTODO: description
    self.displayName = ''

    #: DOCTODO: description
    self.description = ''

    #: DOCTODO: description
    self.version = None

    #: DOCTODO: description
    self.url = ''

    #: object from class implements vcs.IVcs DOCTODO: description
    self.vcs = None

    #: DOCTODO: description
    self.dependsOn = []

    #: DOCTODO: description
    self.deployTo = []

    #: DOCTODO: description
    self.dirName = ''

    #: DOCTODO: description
    self.fileName = ''

    #: DOCTODO: description
    self.env = None

    #: DOCTODO: description
    self.defaultTarget = ''

    #: List of targets passed to Atta in the command line or in the
    #: parameter *targets* of the method :py:meth:`.Project.RunProject`.
    self.targets = []

    #: DOCTODO: description
    self.targetsMap = {}

    # Private stuff.
    self._executedTargets = {}
    self._executedTargetsList = []
    self._targetsLevel = 0
    self._parent = parent

  def Import(self, fileName):
    """TODO: description"""
    moduleName = None
    module = None
    try:
      orgFileName = fileName
      fileName = OS.Path.RemoveExt(os.path.normpath(os.path.realpath(fileName)))
      dirName = os.path.dirname(fileName)
      moduleName = os.path.basename(fileName)
      fileName += '.py'
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
          except Exception: pass
        else:
          packageFileName = None

      prevDirName = self.env.chdir(dirName)
      File._Set(fileName)
      try:
        Atta.Log('  fullModuleName = ' + fullModuleName, level = logLevel)
        Atta.Log('  moduleName = ' + moduleName, level = logLevel)
        Atta.Log('---\n', level = logLevel)

        sys.path.insert(0, dirName)
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
        if prevDirName is not None:
          self.env.chdir(prevDirName)

    except:
      raise

    return moduleName, module

  def ResolveDependencies(self, data = None, scope = Dict.Scopes.compile, returnPackages = True, defaultRepository = None):
    """TODO: description"""
    from . import Dependencies
    resolver = Dependencies.Resolver()
    if resolver.Resolve(self.dependsOn if data is None else data, scope, defaultRepository):
      return resolver.Result() if not returnPackages else (resolver.Result(), resolver.ResultPackages())
    else:
      return None if not returnPackages else (None, None)

  def GetTarget(self, targetClass):
    """TODO: description"""
    targetClass = self._GetTargetClass(targetClass)
    if types.FunctionType == type(targetClass):
      return targetClass
    target = targetClass()
    return target

  def RunTarget(self, targetClass, force = False):
    """TODO: description"""
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
        # Target is a class (and we assume that inherits from (or implements) atta.targets.Base.Target)
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
    """TODO: description"""
    project = Project(self)
    if environ is None:
      environ = self.env
    project._Run(environ, fileName, (targets if targets else []))
    return project

  def CreatePackage(self):
    """TODO: description"""
    return PackageId(self.groupId, self.name, str(self.version), self.type)

  def Deploy(self, baseDirName, files, package, data = None, defaultRepository = None):
    """TODO: description"""
    from . import Deploy
    deployer = Deploy.Deployer()
    return deployer.Deploy(baseDirName, files, package,
                           self.deployTo if data is None else data, defaultRepository)

  '''private section'''

  def AvailableTargets(self, moduleName):
    availableTargets = []
    try:
      for m in dir(sys.modules[moduleName]):
        d = sys.modules[moduleName].__dict__[m]
        if m != 'Target' and m != 'Project' and Dict.dependsOn in dir(d):
          availableTargets.append(m)
    except Exception: pass
    return availableTargets

  def _Run(self, environ, fileName, targets):
    prevDirName = os.getcwd()
    prevAttaProject = _GetProject()
    try:
      self.startTime = datetime.now()

      _SetProject(self)

      if os.path.isdir(fileName):
        fileName = os.path.join(fileName, Dict.defaultBuildFileName)
      self.dirName = os.path.normpath(os.path.realpath(os.path.dirname(fileName)))
      self.fileName = os.path.join(self.dirName, OS.Path.RemoveExt(os.path.basename(fileName)) + '.py')
      if not os.path.exists(self.fileName):
        raise IOError(os.errno.ENOENT, Dict.errFileNotExists % self.fileName)

      self.env = Env.Env(environ)
      self.env.chdir(self.dirName)
      self.name = os.path.basename(self.dirName)
      self.version = Version(createIfNotExists = False)
      self.targets = targets

      if self._parent is None:
        Atta.Log('Buildfile: ' + self.fileName)

      moduleName, module = self.Import(self.fileName)

      if len(targets) <= 0 or len(targets[0]) <= 0:
        targets = [self.defaultTarget]
        if len(targets[0]) <= 0:
          availableTargets = self.AvailableTargets(moduleName)
          if len(availableTargets):
            availableTargets = '\nThe following targets are available:\n  ' + '\n  '.join(availableTargets)
          Atta.Log('\nYou did not specify any target.' + str(availableTargets),
                    project = self.fileName,
                    log = True)
          self._End(Project.SUCCESSFUL)
          return

      self.env._Dump()
      self._Dump()

      Atta.Log(
            project = self.fileName,
            start = True,
            at = self.startTime)

      if self.version is not None:
        self.version._CreateIfNotExists()

      for targetName in targets:
        self._executedTargets.clear() # Behavior compatible with Ant.
        self._targetsLevel = 0
        self.RunTarget(moduleName + '.' + targetName)
        self._DumpExecutedTargets()

      self._End(Project.SUCCESSFUL)

    except Exception as e:
      self._End(Project.FAILED, e)
      raise

    finally:
      _SetProject(prevAttaProject)
      if self.env:
        self.env.chdir(prevDirName)

  def _End(self, status, exception = None):
    self.endTime = datetime.now()
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
    if isinstance(targetClass, basestring):
      tryTargetInProject = True
      while True:
        targetPackage, targetClassName = OS.Path.RemoveExt(targetClass), OS.Path.Ext(targetClass, False)
        try:
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
                # that come with Atta (such as Java or Android).
                targetClass = OS.Path.RemoveExt(os.path.basename(self.fileName)) + '.' + targetPackage
                tryTargetInProject = False
              else:
                key = targetPackage
            if key:
              if self.targetsMap.has_key(key):
                targetClass = self.targetsMap[key]
              else:
                raise AttaError(self, 'Can not find: %s target.' % targetClassName)
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
