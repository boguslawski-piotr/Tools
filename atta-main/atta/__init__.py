## \package  atta
#  \brief    atta implementation
#
# \todo Utility for universal .bat/.sh/.cmd/ etc. invoking (?)
#

__all__ = [
           # Globals
           'atta',
           'project',
           'file',

           # Enums & Classes
           'LogLevel',
           'Project',
           'Target',
           'Task',
           
           # Tasks
           'Echo',
           'Exec',
           'PyExec',
          ]

global atta
atta = None

global project
project = None

global file
file = None

## \defgroup Utils Utils
#

from Log import LogLevel

##  \defgroup Targets Targets
#

from BaseClasses import Target, Task

## \defgroup Tasks Tasks
# All available tasks.
#

from Echo import Echo
from Exec import Exec
from PyExec import PyExec
  