import os
import sys

from ..tools.Misc import LogLevel
from atta import Atta

#------------------------------------------------------------------------------ 

class Target:
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
  
  def Log(self, msg = '', **args):
    self._Log(msg, log = True, **args)
  
  '''private section'''
      
  def _Log(self, msg = '', **args):
    if not hasattr(self, 'name'):
      self.name = '{0}'.format(self.__class__)
      #self.name = self.name[self.name.rfind('.') + 1:len(self.name)]
    Atta.logger.Log(msg, target = self.name, **args)

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
    
    