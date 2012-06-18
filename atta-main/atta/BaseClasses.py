import sys
import os
from datetime import datetime
from atta.Log import LogLevel, Log, LogNM

## Program class 
#  TODO: description
class Program():
  name = 'atta'
  description = ''
  version = None
  
  dirName = None
  args = None

  @staticmethod 
  def Dump():
    Log("Program.args = {0}".format(Program.args), level=LogLevel.DEBUG)

## Env class 
#  TODO: description
class Env():
  @staticmethod
  def chdir(path):
    os.chdir(path)
    setattr(Env, 'cwd', os.getcwd())
    
  @staticmethod
  def SetAttrsFromSystem():
    for key, value in os.environ.iteritems():
      setattr(Env, key, value)
     
  @staticmethod 
  def Dump():
    Log('Env.cwd = ' + Env.cwd, level=LogLevel.DEBUG)
    for key, value in os.environ.iteritems():
      Log('Env.' + key + ' = ' + value, level=LogLevel.DEBUG)

## Project class 
#  TODO: description
class Project():
  dirName = ''
  fileName = ''
  
  name = ''
  description = ''

  defaultTarget = ''
  
  @staticmethod
  def Dump():
    Log('Project.dirName = ' + Project.dirName, level=LogLevel.DEBUG)
    Log('Project.fileName = ' + Project.fileName, level=LogLevel.DEBUG)
    
## Base class for all targets.
#  TODO: description
class Target:
  DependsOn = []
  
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
    
## Build class
#  TODO: description
class Build:
  SUCCESSFUL = 0
  FAILED = 1
  
  executedTargets = {}
  
  def Start(self):
    self.startTime = datetime.now()
    LogNM(build=Project.fileName,
          start=True,
          at=self.startTime)
    return
  
  def _Run(self, targetClass):
    if not Build.executedTargets.has_key(targetClass.__name__):
      Build.executedTargets[targetClass.__name__] = targetClass()
      for dependClass in Build.executedTargets[targetClass.__name__].DependsOn:
        self._Run(dependClass)
      Build.executedTargets[targetClass.__name__]._Run()
    return
  
  def Run(self, targetClass):
    Build.executedTargets = {}
    self._Run(targetClass)
    return
  
  def End(self, status, exception = None):
    self.endTime = datetime.now();
    LogNM(build=Project.fileName,
          end=True,
          status=('SUCCESSFUL' if status == Build.SUCCESSFUL else 'FAILED!'),
          at=self.endTime,
          time=self.endTime - self.startTime,
          exception=exception,
          level=LogLevel.ERROR)
    return
  
  def ParseScript(self, script):
    return script
