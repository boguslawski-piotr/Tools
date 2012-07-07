'''.. no-user-reference:'''
import os
import platform

from ..tools.OS import Path
from ..Activity import Activity
from .. import GetProject

class Target(Activity):
  '''
  Base class for all targets.
     
  TODO: description
  '''

  dependsOn = []
  '''TODO: description'''

  system = []
  '''TODO: description'''
  
  def CanRun(self):
    '''TODO: description'''
    canRun = True
    if len(self.system) > 0:
      canRun = False
      system = platform.system().lower()
      tsystem = Path.AsList(self.system, ',')
      for s in tsystem:
        if s.lower() in system:
          canRun = True
          break
    return canRun
  
  '''
  Method 'Prepare' maybe be defined in a class that inherits from the Target. Then will start.
  When it returns False, project will not run any targets from 
  the section 'dependsOn' as well as the Run method.
  '''
  #def Prepare(self):
  #  return True
  
  def Run(self):
    '''TODO: description'''
    pass
  
  '''
  Method 'Finalize' maybe be defined in a class that inherits from the Target. Then will start.
  '''
  #def Finalize(self):
  #  pass
  
  '''private section'''
      
  def _Type(self):
    return 'target'
  
  def _Name(self):
    if not hasattr(self, 'name'):
      self.name = '{0}'.format(self.__class__)
      self.name = self.name.replace('atta.targets.', '')
      project = GetProject()
      if project._parent is None:
        self.name = self.name.replace(Path.RemoveExt(os.path.basename(project.fileName)) + '.', '')
    return self.name
  
  def _RunPrepare(self):
    if 'Prepare' in dir(self):
      self._Log(prepare = True)
      return self.Prepare()
    return True
  
  def _Run(self):
    if not hasattr(self, 'wasExecuted') or not self.wasExecuted:
      self._Log(start = True)
      self.Run()
      self._Log(end = True)
    self.wasExecuted = True
    
  def _RunFinalize(self):
    if 'Finalize' in dir(self):
      self._Log(finalize = True)
      self.Finalize()
      