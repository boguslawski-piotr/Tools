# Public interface (exports)

__all__ = [
           # Environment
           'Atta',
           'AttaError',
           'Project',
           'GetProject',
           'File',

           # Enums & Classes
           'Target',
           'Task',
           
           # Tools
           'LogLevel',
           'Properties',
           'FileSet',
           'DirSet',
           'OS',

           # Tasks
           'Echo',
           
           'Exec',
           'PyExec',
           
           'Archive',
           'Zip',
           
           'Javac',
           'Jar',
          ]

# Atta

from tools.Misc import LogLevel, Logger, VariablesExpander
import loggers.Std
import tools.VariablesLikeAntExpander
from version import attaVersionName
  
class AttaError(RuntimeError): 
  '''Base class for all exceptions thrown by Atta.'''
  def __init__(self, caller, msg):
    self.caller = caller
    self.msg = msg
    
  def __str__(self):
    return '{0}:\n{1}'.format(self.caller.__class__, self.msg)

class Atta:
  '''
  Provides basic information about Atta. 
  Also provides a few simple tools.
  '''
  name        = 'Atta'
  description = 'Build tool in pure Python.'
  
  versionName = attaVersionName
  '''TODO: description'''
  
  version = int(attaVersionName.replace('.', ''))  
  '''TODO: description'''
  
  dirName = None
  '''TODO: description'''
  
  logger = Logger(loggers.Std.Logger)
  '''TODO: description'''
  
  variablesExpander = VariablesExpander(tools.VariablesLikeAntExpander.Expander) 
  '''TODO: description'''
  
  props = None
  '''TODO: description'''

# Project property 

Project = None
'''Provides access to data and general tools for the entire project.
   Use it ONLY during the phase of interpreting the main build script.  
   Property Project is an instance of the class :py:class:`atta.Project`.'''

def GetProject():
  '''Provides access to data and general tools for the entire project. 
     Returns an instance of the class :py:class:`atta.Project`.'''
  return Project

# File property 

class File:
  '''Describes currently interpreted build script.'''
  
  name = ''
  '''
  Full file name.
  
  Property File.name is available only during 
  the phase of interpreting the build script. 
  NOT when Atta performing tasks.
  '''
  
  '''private section'''
  
  _list = []
  
  @staticmethod
  def _Set(fileName):
    File._list.append(File.name)
    File.name = fileName
 
  @staticmethod
  def _Unset():
    File.name = File._list.pop()
    
# Tools

from tools.Sets import FileSet, DirSet
from tools.Properties import Properties
from tools import OS as OS

# Base classes

from targets.Base import Target
from tasks.Base import Task

# Tasks
# All available tasks.

from tasks.Echo import Echo

from tasks.Exec import Exec
from tasks.PyExec import PyExec

from tasks.Archive import Archive
from tasks.Zip import Zip

from tasks.Javac import Javac
from tasks.Jar import Jar

  