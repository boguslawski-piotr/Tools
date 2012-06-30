'''.. Miscellaneous: Echoes a message: echo'''
import sys
import os
import stat
import re

from ..tasks.Base import Task
from ..tools.Misc import LogLevel, isiterable
import atta

class Echo(Task):
  '''
  Echoes a message to the current logger. A level can be specified, 
  which controls at what logging level the message is filtered at.
  The task can also echo to a file, in which case the option to 
  append rather than overwrite the file is available, 
  and the level option is ignored. |Ant|

  Parameters:
  
  * **msg**   The message to echo. 
    It can be any object that can be converted to string, a iterable or a file-like object. (default: blank line)
  
  * **level** Control the log level at which this message is reported. 
    (default: :py:attr:`.LogLevel.WARNING`)
  
  * **file**   The file name or a file-like object to write the message to. |None|
  * **append** Append to an existing file? |False|
  * **force**  Overwrite read-only file? |False|

  '''
  def __init__(self, msg = '', **tparams):
    level = tparams.get('level', LogLevel.WARNING)
    _file = tparams.get('file', None)
    if isinstance(msg, basestring):
      msg = self.ExpandVariables(msg, **tparams)
    
    if _file is None:
      if isiterable(msg):
        for line in msg:
          if isinstance(line, basestring):
            line = self.ExpandVariables(line, **tparams)
          self.Log(line, level = level)
      else:
        self.Log(msg, level = level)
    else:
      append = tparams.get('append', False)
      force = tparams.get('force', False)
      
      if isinstance(_file, basestring):
        if os.path.exists(_file) and force:
          st = os.stat(_file)
          os.chmod(_file, stat.S_IMODE(st.st_mode) | stat.S_IWRITE)
        if append: mode = 'a+b'
        else: mode = 'w+b'
        _f = open(_file, mode)
      else:
        _f = _file
        if append:
          _f.seek(0, os.SEEK_END)
      
      if isiterable(msg):
        for line in msg:
          if isinstance(line, basestring):
            line = self.ExpandVariables(line, **tparams)
          _f.write(line)
      else:
        _f.write(msg)
      
      if isinstance(_file, basestring):
        _f.close()
