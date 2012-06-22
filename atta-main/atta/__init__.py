'''Atta interface for build scripts'''

__all__ = [
           # Environment
           'attai',
           'project',
           'file',

           # Enums & Classes
           'Project',
           'Target',
           'Task',
           
           # Tools
           'LogLevel',
           'Properties',
           'FileSet',
           'DirSet',

           # Tasks
           'Echo',
           'Exec',
           'PyExec',
          ]

# Environment

global attai
attai = None

global project
project = None

global file
file = None

# Tools

from Log import LogLevel
from tools.Sets import FileSet, DirSet
from tools.Properties import Properties

# Base classes

from BaseClasses import Target, Task

# Targets
# All available targets and targets groups.

# Tasks
# All available tasks.

from tasks.Echo import Echo
from tasks.Exec import Exec
from tasks.PyExec import PyExec
  