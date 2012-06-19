## \package Echo 
#  \brief   Echo task
#  \ingroup Tasks 
#
# \task{Echo([msg, **tparams])}
#
# \param  msg     The message to echo.
#                 \type any object that can be converted to string 
#                 \def blank line
# 
# \tparam level   Control the log level at which this message is reported.
#                 \type \link atta.Log.LogLevel LogLevel \endlink
#                 \def INFO
#          
# \tparam file    The file name or a file-like object to write the message to.
#                 \type string or file-like class 
#                 \def None
#
# \tparam append  Append to an existing file?
#                 \type boolean
#                 \def False
#
# \tparam force   Overwrite read-only file?
#                 \type boolean 
#                 \def False
#
# \uc test_echo.py
#
# \impl{atta.Echo.Echo}
#
# \author Piotr Boguslawski (boguslawski.piotr@gmail.com)
#
# \example test_echo.py
# Echo task use cases.

import os
import stat

from BaseClasses import Task
from Log import LogLevel

## Echo task implementation
class Echo(Task):
  def __init__(self, msg = '', **tparams):  
    level = tparams.get('level', LogLevel.INFO)
    _file = tparams.get('file', None)
    
    if _file is None:
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
      
      _f.write(msg)
      
      if isinstance(_file, basestring):
        _f.close()
        