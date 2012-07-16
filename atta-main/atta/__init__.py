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
           'DirFileSet',
           'ExtendedFileSet',
           'OS',
           'Version',
           'Xml',
           'XmlElement',

           'PackageId',

           # Tasks
           'Echo',
           'Delete',
           'Filter',
           'Copy',
           'Move',

           'Exec',
           'PyExec',

           'Archive',
           'Zip',

           'Javac',
           'Jar',

           'Git',
          ]

# Atta

from .tools.Misc import VarsExpander
from .loggers import LogLevel, Logger, Std
from .tools import DefaultVarsExpander
from . import version

class AttaError(RuntimeError):
  """Base class for all exceptions thrown by Atta."""
  def __init__(self, caller, msg):
    self.caller = caller
    self.msg = msg

  def __str__(self):
    return '{0}:\n{1}'.format(self.caller.__class__ if self.caller else 'Atta', self.msg)

class Atta:
  """
  Provides basic information about Atta.
  Also provides a few simple tools.
  """
  name = 'Atta'
  description = 'Build tool in pure Python.'

  #: DOCTODO: description
  version = version.__version__

  #: DOCTODO: description
  versionInt = int(version.replace('.', ''))

  #: DOCTODO: description
  dirName = None

  _logger = Logger(Std.Logger)

  @staticmethod
  def Logger():
    """TODO: description"""
    return Atta._logger

  @staticmethod
  def LogLevel():
    """TODO: description"""
    return Atta._logger.GetLevel()

  @staticmethod
  def Log(msg = '', **tparams):
    """TODO: description"""
    Atta._logger.Log(msg, **tparams)

  @staticmethod
  def LogIterable(msg, iterable, **tparams):
    """TODO: description"""
    Atta._logger.LogIterable(msg, iterable, **tparams)

  _varsExpander = VarsExpander(DefaultVarsExpander.Expander)

  @staticmethod
  def VarsExpander():
    """TODO: description"""
    return Atta._varsExpander

  @staticmethod
  def ExpandVars(data, **tparams):
    """DOCTODO: description"""
    return Atta.VarsExpander().Expand(data, **tparams)

  _props = None

  @staticmethod
  def Props():
    """All Atta settings (properties) as dictionary. DOCTODO: more description"""
    return Atta._props

  @staticmethod
  def _SetProps(props):
    Atta._props = props

# Project property

#: Provides access to data and general tools for the entire project.
#: Use it ONLY during the phase of interpreting the main build script.
#: Property Project is an instance of the class :py:class:`atta.Project`.
Project = None

def GetProject():
  """Provides access to data and general tools for the entire project.
     Returns an instance of the class :py:class:`atta.Project`."""
  return Project

def _SetProject(project):
  global Project
  Project = project

# File property

class File:
  """Describes currently interpreted build script."""

  #: Full file name. Available only during
  #: the phase of interpreting the build script.
  #: NOT when Atta performing targets & tasks.
  name = ''

  # private section

  _list = []

  @staticmethod
  def _Set(fileName):
    File._list.append(File.name)
    File.name = fileName

  @staticmethod
  def _Unset():
    File.name = File._list.pop()

# Tools

from .tools.Sets import FileSet, DirSet, DirFileSet, ExtendedFileSet
from .tools.Properties import Properties
from .tools import OS as OS
from .tools.Ver import Version
from .tools.Xml import Xml, XmlElement

from .repositories.Package import PackageId

# Base classes

from .targets.Base import Target
from .tasks.Base import Task

# All available tasks.

from .tasks.Echo import Echo

from .tasks.Delete import Delete
from .tasks.Filter import Filter
from .tasks.Copy import Copy
from .tasks.Move import Move

from .tasks.Exec import Exec
from .tasks.PyExec import PyExec

from .tasks.Archive import Archive
from .tasks.Zip import Zip

from .tasks.Javac import Javac
from .tasks.Jar import Jar

from .dvcs.Git import Git
