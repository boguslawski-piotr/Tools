# Public interface (exports)

__all__ = [
           # Environment
           'Atta',
           'Project',
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
           
           'Javac',
           'Jar',
          ]

# Atta

from tools.Misc import LogLevel, Logger
from tools.Misc import VariablesExpander

import loggers.StdLogger
import tools.VariablesLikeAntExpander
from version import attaVersionName
  
class Atta:
  '''
  Provides basic information about Atta. 
  Also provides a few simple tools.
  '''
  name        = 'Atta'
  description = 'Cool and funny build system in pure Python.'
  
  versionName = attaVersionName
  '''TODO: description'''
  
  version = int(attaVersionName.replace('.', ''))  
  '''TODO: desc...'''
  
  dirName = None
  '''TODO: desc...'''
  
  logger = Logger(loggers.StdLogger.Logger)
  '''TODO: desc...'''
  
  variablesExpander = VariablesExpander(tools.VariablesLikeAntExpander.Expander) 
  '''TODO: desc...'''
  
# Project property 

Project = None
'''
Provides access to data and general tools for the entire project. 
Property Project is an instance of the class :py:class:`atta.Project`.
'''

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

from tasks.Javac import Javac
from tasks.Jar import Jar

  