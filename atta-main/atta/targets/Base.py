import os
import platform

from ..tools.OS import Path
from ..Activity import Activity
from atta import Atta, GetProject

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
  
  def Prepare(self):
    return True
  
  def Run(self):
    pass
  
  def Finalize(self):
    return True
  
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
  
  def _Run(self):
    if not hasattr(self, 'wasExecuted') or not self.wasExecuted:
      self._Log(prepare = True)
      if self.Prepare():
        self._Log(start = True)
        self.Run()
        self._Log(finalize = True)
        self.Finalize()
        self._Log(end = True)
    self.wasExecuted = True
    
    