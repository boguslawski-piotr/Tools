""".. Local: TODO"""
import os

from ..loggers import Compact
from .. import Atta, AttaError, LogLevel, Dict, OS, Task
from . import Local

class Repository(Local.Repository):
  """TODO: description"""

  def vPrepareFileName(self, fileName):
    return os.path.normpath(os.path.join(self.Project().dirName, fileName))

  def Get(self, package, scope, store = None):
    projectName = self.data.get(Dict.project)
    if not projectName:
      raise AttaError(self, 'Not given name / directory of the project.')

    if os.path.isdir(projectName):
      dirName = projectName
      projectName = projectName + '/' + Dict.defaultBuildFileName
    else:
      dirName = os.path.dirname(projectName)
    if not os.path.exists(projectName):
      raise AttaError(self, Dict.errFileNotExists % projectName)

    targetNames = OS.Path.AsList(self.data.get('target', ['package']), ' ')
    resultProperties = self.data.get(Dict.resultIn, ['packageName'])
    result = None

    projectTmpName = OS.Path.TempName(dirName, 'py')
    try:
      OS.CopyFile(projectName, projectTmpName)
    except:
      pass
    else:
      prevLoggerClass = Atta.Logger().SetImpl(Compact.Logger)
      try:
        # Invoke Atta project.
        Atta.Log(target = self._Name(), prepare = True, level = LogLevel.VERBOSE)
        self.Log('Invoking target(s): %s in: %s' % (' '.join(targetNames), projectName), level = LogLevel.VERBOSE)

        project = self.Project().RunProject(self.Project().env, projectTmpName, targetNames)

        Atta.Log(target = self._Name(), prepare = True, level = LogLevel.VERBOSE)
        self.Log('Back in: %s' % self.Project().fileName, level = LogLevel.VERBOSE)

        # Collect produced file(s).
        result = []
        resultProperties = OS.Path.AsList(resultProperties)
        for propertyName in resultProperties:
          r = getattr(project, propertyName, None)
          if r:
            r = OS.Path.AsList(r)
            for i in range(0, len(r)):
              if not os.path.exists(r[i]):
                r[i] = os.path.join(dirName, r[i])
            result += r

        # Prepare valid package if it's possible.
        package.groupId = getattr(project, Dict.groupId, None)
        package.artifactId = getattr(project, Dict.name, None)
        package.version = str(getattr(project, Dict.version, None))
        #package.type = str(getattr(project, Dict.type, None)) # TODO: ?
        package.type = None
        if result:
          package.systemPath = '\\${pathTo' + (package.artifactId if package.artifactId else '') + '}'
          package.scope = Dict.system

      finally:
        Atta.Logger().SetImpl(prevLoggerClass)
        OS.RemoveFile(projectTmpName)
        OS.RemoveFile(projectTmpName + 'c')
        OS.RemoveFile(projectTmpName + 'o')

    if not result:
      msg = 'Target(s): %s in: %s returned no information in: %s' % (' '.join(targetNames), projectName, resultProperties)
      if not package.IsOptional():
        raise AttaError(self, msg)
      else:
        self.Log(msg, level = LogLevel.WARNING)

    self.Log(Dict.msgReturns % OS.Path.FromList(result), level = LogLevel.DEBUG)
    return result

  def _Name(self):
    name = Task._Name(self)
    return 'Project.' + name
