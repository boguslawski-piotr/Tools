""".. Miscellaneous: Echoes a message: echo"""
import os

from ..tools.Misc import isiterable
from .. import Dict, LogLevel, Task, OS

class Echo(Task):
  """
  Echoes a message to the current logger. A level can be specified,
  which controls at what logging level the message is filtered at.
  The task can also echo to a file, in which case the option to
  append rather than overwrite the file is available,
  and the level option is ignored. |Ant|

  Parameters:

  * **msg** `(blank line)` - The message to echo.
    It can be any object that can be converted to string, a iterable or a file-like object.

  * **expandVars** |True|  - Expand variables?
  * **file** |None|        - The file name or a file-like object to write the message to.
  * **append** |False|     - Append to an existing file?
  * **force** |False|      - Overwrite read-only file?

  * **level** `(`:py:attr:`.LogLevel.INFO`\ `)` - Control the log level at which this message is reported.

  """
  def __init__(self, msg = '', **tparams):
    level = tparams.get(Dict.paramLevel, LogLevel.INFO)
    file = tparams.get('file', None)
    expandVars = tparams.get('expandVars', True)

    if isinstance(msg, basestring) and expandVars:
      msg = self.ExpandVars(msg, **tparams)

    if file is None:
      if isiterable(msg):
        for line in msg:
          if isinstance(line, basestring) and expandVars:
            line = self.ExpandVars(line, **tparams)
          self.Log(line, level = level)
      else:
        self.Log(msg, level = level)
    else:
      append = tparams.get('append', False)
      force = tparams.get('force', False)

      if isinstance(file, basestring):
        if force:
          OS.SetReadOnly(file, False)
        if append: mode = 'a+b'
        else: mode = 'w+b'
        _f = open(file, mode)
      else:
        _f = file
        if append:
          _f.seek(0, os.SEEK_END)

      if isiterable(msg):
        for line in msg:
          if isinstance(line, basestring) and expandVars:
            line = self.ExpandVars(line, **tparams)
          _f.write(line)
      else:
        _f.write(msg)

      if isinstance(file, basestring):
        _f.close()
