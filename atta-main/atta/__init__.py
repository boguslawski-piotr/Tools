## \package  atta
#  \brief    atta implementation
#
# \todo Utility for universal .bat/.sh/.cmd/ etc. invoking (?)
#

__all__ = [
           # Enums & Classes
           'LogLevel',
           'Env',
           'Project',
           'Target',
           
           # Tasks
           'Echo',
           'Exec',
           'PyExec'
          ]

## \defgroup Utils Utils
#

from Log import LogLevel

##  \defgroup Targets Targets
#

from BaseClasses import Env, Project, Target

## \defgroup Tasks Tasks
# All available tasks.
#

from Echo import Echo
from Exec import Exec
from PyExec import PyExec
  
