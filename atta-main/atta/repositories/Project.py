'''.. Local: TODO'''
import os
import shutil

import atta.tools.OS as OS
from ..tasks.Base import Task
from ..tools.Misc import LogLevel
from ..loggers import Compact
from atta import Atta, AttaError, GetProject
import Local

class Repository(Local.Repository):
  '''TODO: description'''
  
  def VPrepareFileName(self, fileName):
    return os.path.normpath(os.path.join(GetProject().dirName, fileName))

  def Get(self, packageId, store = None):
    if packageId.groupId is None:
      raise AttaError(self, 'Not given name / directory of the project (grupId entry).')
    
    if os.path.isdir(packageId.groupId):
      projectName = packageId.groupId + '/build.py'
      dirName = packageId.groupId
    else:
      projectName = packageId.groupId
      dirName = os.path.dirname(projectName)
    if not os.path.exists(projectName):
      raise AttaError(self, 'File: %s does not exists!' % projectName)
    
    targetNames = OS.Path.AsList(self.data.get('target', ['package']), ' ')
    resultPropertyName = self.data.get('resultIn', 'packageName')
    result = None
    
    projectTmpName = dirName + '/' + OS.Path.TempName(dirName, 'py')
    try:
      shutil.copy2(projectName, projectTmpName)
    except:
      pass
    else:
      prevLoggerClass = Atta.logger.SetImpl(Compact.Logger)
      try:
        Atta.logger.Log(target = self._Name(), prepare = True, level = LogLevel.VERBOSE)
        self.Log('Invoking target(s): %s in: %s' % (' '.join(targetNames), projectName), level = LogLevel.VERBOSE)
        
        project = GetProject().RunProject(GetProject().env, projectTmpName, targetNames)
        
        Atta.logger.Log(target = self._Name(), prepare = True, level = LogLevel.VERBOSE)
        self.Log('Back in: %s' % (GetProject().fileName), level = LogLevel.VERBOSE)
        
        result = getattr(project, resultPropertyName, None)
        if result is not None:
          result = OS.Path.AsList(result)
          for i in range(0, len(result)):
            if not os.path.exists(result[i]):
              result[i] = os.path.join(dirName, result[i])
      except:
        raise
      finally:
        Atta.logger.SetImpl(prevLoggerClass)
        OS.RemoveFile(projectTmpName)
        OS.RemoveFile(projectTmpName + 'c')
        OS.RemoveFile(projectTmpName + 'o')
    
    if result is None:
      raise AttaError(self, 'Target(s): %s in: %s returned no information in: %s' % (' '.join(targetNames), projectName, resultPropertyName))
    
    self.Log('Returns: %s' % OS.Path.FromList(result), level = LogLevel.VERBOSE)
    return result

  def _Name(self):
    name = Task._Name(self)
    return 'Project.' + name
