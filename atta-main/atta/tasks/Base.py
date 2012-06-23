import os
import sys

from ..tools.Misc import LogLevel
from atta import Atta

#------------------------------------------------------------------------------ 

class Task:
  '''
  Base class for all tasks.
     
  TODO: description
  '''
  def Log(self, msg = '', **args):
    self._Log(msg, **args)
  
  def ExpandVariables(self, txt, **tparams):
    return Atta.variablesExpander.Expand(txt, **tparams)
    
  '''private section'''
    
  def _Log(self, msg = '', **args):
    if not hasattr(self, 'name'):
      self.name = '{0}'.format(self.__class__)
      self.name = self.name[self.name.rfind('.') + 1:len(self.name)]
    Atta.logger.Log(msg, task = self.name, **args)

  def __enter__(self):
    return self
  
  def __exit__(self, type, value, traceback):
    return self
    
