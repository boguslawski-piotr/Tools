# Public interface (exports)

__all__ = [
           # Environment
           'Atta',
           'AttaError',
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

           'Git',
          ]

# Atta

from .tools import DefaultVarsExpander as DVE
from .tools import VarsExpander as VE
from .loggers import Logger as _Logger, Std
from . import version as _version

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
  version = _version.__version__

  #: DOCTODO: description
  versionInt = int(version.replace('.', ''))

  #: DOCTODO: description
  dirName = None

  _logger = _Logger(Std.Logger)

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

  _varsExpander = VE.VarsExpander(DVE.Expander)

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
#: Inside classes that inherits from :py:class:`.Target` please use the *self.Project*.
#: Property Project is an instance of the class :py:class:`atta.Project`.
Project = None

def _GetProject():
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

# Quite strange constructions for the following reasons:
# - ide PyCharm not report warnings :)
# - it will be easier in the future to change the implementation

# Tools

from . import loggers
LogLevel = loggers.LogLevel

from .tools import Sets
FileSet = Sets.FileSet
DirSet = Sets.DirSet
DirFileSet = Sets.DirFileSet
ExtendedFileSet = Sets.ExtendedFileSet

from .tools import Properties
Properties = Properties.Properties

from .tools import OS

from .tools import Ver
Version = Ver.Version

from .tools import Xml
XmlElement = Xml.XmlElement
Xml = Xml.Xml

from .repositories import Package
PackageId = Package.PackageId

# Base classes

from .targets import Base as TargetB
Target = TargetB.Target
from .tasks import Base as TaskB
Task = TaskB.Task

# All core tasks.

from .tasks import Echo, Delete, Filter, Copy, Move
Echo = Echo.Echo
Delete = Delete.Delete
Filter = Filter.Filter
Copy = Copy.Copy
Move = Move.Move

from .tasks import Exec, PyExec
Exec = Exec.Exec
PyExec = PyExec.PyExec

from .tasks import Archive, Zip
Archive = Archive.Archive
Zip = Zip.Zip

from .vcs import Git
Git = Git.Git
