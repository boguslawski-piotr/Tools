'''.. Local: TODO'''
import os
import shutil

from ..tasks.Base import Task
from ..tools.Misc import LogLevel
from ..tools import OS
from ..loggers import Compact
from .. import Atta, AttaError, GetProject, Dict
from . import Local

class Repository(Local.Repository):
  '''TODO: description'''
  
  def vPrepareFileName(self, fileName):
    return os.path.normpath(os.path.join(GetProject().dirName, fileName))

  def Get(self, packageId, scope, store = None):
    if packageId.groupId is None:
      raise AttaError(self, 'Not given name / directory of the project (grupId entry).')
    
    if os.path.isdir(packageId.groupId):
      projectName = packageId.groupId + '/' + Dict.defaultBuildFileName
      dirName = packageId.groupId
    else:
      projectName = packageId.groupId
      dirName = os.path.dirname(projectName)
    if not os.path.exists(projectName):
      raise AttaError(self, Dict.errFileNotExists % projectName)
    
    targetNames = OS.Path.AsList(self.data.get('target', ['package']), ' ')
    resultProperties = self.data.get(Dict.resultIn, ['packageName'])
    result = None
    
    projectTmpName = dirName + '/' + OS.Path.TempName(dirName, 'py')
    try:
      shutil.copy2(projectName, projectTmpName)
    except:
      pass
    else:
      prevLoggerClass = Atta.Logger().SetImpl(Compact.Logger)
      try:
        # Invoke Atta project.
        Atta.Log(target = self._Name(), prepare = True, level = LogLevel.VERBOSE)
        self.Log('Invoking target(s): %s in: %s' % (' '.join(targetNames), projectName), level = LogLevel.VERBOSE)
        
        project = GetProject().RunProject(GetProject().env, projectTmpName, targetNames)
        
        Atta.Log(target = self._Name(), prepare = True, level = LogLevel.VERBOSE)
        self.Log('Back in: %s' % (GetProject().fileName), level = LogLevel.VERBOSE)
        
        # Collect produced file(s).
        result = []
        resultProperties = OS.Path.AsList(resultProperties)
        for propertyName in resultProperties:
          r = getattr(project, propertyName, None)
          if r != None:
            r = OS.Path.AsList(r)
            for i in range(0, len(r)):
              if not os.path.exists(r[i]):
                r[i] = os.path.join(dirName, r[i])
            result += r
            
        # Prepare valid packageId if it's possible.
        packageId.groupId = getattr(project, Dict.groupId, None)
        packageId.artifactId = getattr(project, Dict.name, None)
        packageId.version = str(getattr(project, Dict.version, None))
        packageId.type = None
        if result != None and len(result) > 0:
          packageId.systemPath = '\\${pathTo' + (packageId.artifactId if packageId.artifactId != None else '') + '}'
          packageId.scope = Dict.system
          # We assume that the main file of the project is always the first on the list.
#          packageId.systemPath = OS.Path.NormUnix(os.path.realpath(result[0]))
#          packageId.type = OS.Path.Ext(packageId.systemPath)
        
      except:
        raise
      finally:
        Atta.Logger().SetImpl(prevLoggerClass)
        OS.RemoveFile(projectTmpName)
        OS.RemoveFile(projectTmpName + 'c')
        OS.RemoveFile(projectTmpName + 'o')
    
    if result is None:
      raise AttaError(self, 'Target(s): %s in: %s returned no information in: %s' % (' '.join(targetNames), projectName, resultProperties))
    
    self.Log('Returns: %s' % OS.Path.FromList(result), level = LogLevel.VERBOSE)
    return result

  def _Name(self):
    name = Task._Name(self)
    return 'Project.' + name
