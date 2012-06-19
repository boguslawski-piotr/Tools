import os
import sys

from OS import *
from Log import LogLevel, Log, LogNM

## Base class for all targets.
#  TODO: description
class Target:
  DependsOn = []
  OsFamily = []
  
  def __init__(self):
    self.name = '{0}'.format(self.__class__)
    self.name = self.name[self.name.rfind('.') + 1:len(self.name)]
    
  def Prepare(self):
    return True
  
  def Run(self):
    pass
  
  def Finalize(self):
    return True
  
  def _Run(self):
    if not hasattr(self, 'wasExecuted') or not self.wasExecuted:
      LogNM(target = self.name, prepare = True)
      if self.Prepare():
        LogNM(target = self.name, start = True)
        self.Run()
        LogNM(target = self.name, finalize = True)
        self.Finalize()
        LogNM(target = self.name, end = True)
    self.wasExecuted = True
    
## Base class for all tasks.
#  TODO: description
class Task:
  def Log(self, msg, **args):
    if not hasattr(self, 'name'):
      self.name = '{0}'.format(self.__class__)
      self.name = self.name[self.name.rfind('.') + 1:len(self.name)]
    Log(msg, task = self.name, **args)
  
  def __enter__(self):
    return self
  
  def __exit__(self, type, value, traceback):
    return self
    
