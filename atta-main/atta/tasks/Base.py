import os
import sys

from ..tools.Misc import LogLevel
from ..Interfaces import Activity
from atta import Atta

#------------------------------------------------------------------------------ 

class Task(Activity):
  '''
  Base class for all tasks.
     
  TODO: description
  '''
  def ExpandVariables(self, txt, **tparams):
    return Atta.variablesExpander.Expand(txt, **tparams)
    
  '''private section'''
    
  def _Type(self):
    return 'task'
  
  def _Name(self):
    if not hasattr(self, 'name'):
      self.name = '{0}'.format(self.__class__)
      self.name = self.name[self.name.rfind('.') + 1:len(self.name)]
    return self.name
  
  def __enter__(self):
    return self
  
  def __exit__(self, exc_type, exc_value, traceback):
    return self
    
