## \package  atta
#  \brief    atta implementation
#

__all__ = [
           # Environment
           'attai',
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

## \defgroup Env Environment
#

global attai
attai = None

global project
project = None

global file
file = None

## \defgroup Utils Utils
#

from Log import LogLevel

##  \defgroup Base Base classes
#

from BaseClasses import Target, Task

## \defgroup Targets Targets and target groups
# All available targets and targets groups.
#

## \defgroup Tasks Tasks
# All available tasks.
#

from Echo import Echo
from Exec import Exec
from PyExec import PyExec
  