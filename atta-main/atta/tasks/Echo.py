import sys
import os
import stat
import re

from ..tasks.Base import Task
from ..tools.Misc import LogLevel
import atta

class Echo(Task):
  '''
  .. snippet:: Echo
  
    .. code-block:: python
  
      Echo([msg, **tparams])
      
    Echoes a message to the current logger. A level can be specified, 
    which controls at what logging level the message is filtered at.
    The task can also echo to a file, in which case the option to 
    append rather than overwrite the file is available, 
    and the level option is ignored. |Ant|
  
    :param  msg:           The message to echo (default: blank line).
    :type msg:             any object that can be converted to string or iterable

    :param LogLevel level: Control the log level at which this message is reported (default: INFO).

    :param file:           The file name or a file-like object to write the message to |None|.
    :type file:            string or file-like class 

    :param boolean append: Append to an existing file |False|.

    :param boolean force:  Overwrite read-only file |False|.
  
    Use cases:
  
    .. literalinclude:: ../../../tests/test_echo.py
  
  '''
  def __init__(self, msg = '', **tparams):  
    isiterable = lambda msg: \
                  not isinstance(msg, basestring) or getattr(msg, '__iter__', False)

    level = tparams.get('level', LogLevel.INFO)
    _file = tparams.get('file', None)
    if isinstance(msg, basestring):
      msg = self.ExpandVariables(msg, **tparams)
    
    if _file is None:
      if isiterable(msg):
        self.LogIterable(None, msg, level = level)
      else:
        self.Log(msg, level = level)
    else:
      append = tparams.get('append', False)
      force = tparams.get('force', False)
      
      if isinstance(_file, basestring):
        if force:
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
        # TODO: how should it work!?
        _f.write(msg)
      else:
        _f.write(msg)
      
      if isinstance(_file, basestring):
        _f.close()
