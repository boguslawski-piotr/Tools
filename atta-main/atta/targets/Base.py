import os
import sys

from ..tools.Misc import LogLevel
from ..Interfaces import Activity
from atta import Atta

#------------------------------------------------------------------------------ 

class Target(Activity):
  '''
  Base class for all targets.
     
  TODO: description
  '''

  DependsOn = []
  OsFamily = []
  
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
      #self.name = '.'.join(self.name.split('.')[-2:])
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
    
    