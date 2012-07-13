'''.. Files, directories: Copies files: copy'''
import os
import shutil
import hashlib
from datetime import datetime, timedelta

from ..tools.Misc import LogLevel
from ..tools import OS
from .. import Dict
from .Filter import Filter

class Copy(Filter):
  '''
  TODO: description
  Uses Filter task.
  Always in binary mode.
  
  * **preserveLastModified** - TODO |True|
  * **copyStat** - TODO |True|
  * **overwrite** - Overwrite existing files even if the destination files are newer. |False|
  * **granularity** - The number of seconds leeway to give before deciding a file is out of date. Def: 1s
  * **useHash** - TODO
  '''
  def __init__(self, srcs, dest, **tparams):
    # Parameters.
    self.preserveLastModified = tparams.get('preserveLastModified', True)
    self.copyStat = tparams.get('copyStat', True)
    self.overwrite = tparams.get('overwrite', False)
    self.granularity = tparams.get('granularity', 1)
    self.useHash = tparams.get('useHash', False)
     
    # The filter that determines whether a file is to be copied.
    def FileFilter(srcFileName, destFileName, **tparams):
      if self.overwrite or not os.path.exists(destFileName):
        return True
      else:
        if self.useHash:
          srcHash = OS.FileHash(srcFileName, hashlib.sha1())
          destHash = OS.FileHash(destFileName, hashlib.sha1())
          return srcHash != destHash
        else:
          srcTime = datetime.fromtimestamp(os.path.getmtime(srcFileName))
          destTime = datetime.fromtimestamp(os.path.getmtime(destFileName))
          return abs((srcTime - destTime)) > timedelta(seconds = self.granularity)

    # Register above filter(s) for Filter task.
    fileFilters = OS.Path.AsList(tparams.get('fileFilters', None))
    fileFilters.append(FileFilter)
    tparams['fileFilters'] = fileFilters
    
    # Always binary mode.
    tparams['binaryMode'] = True
    
    # Copy files.
    Filter.__init__(self, srcs, dest, **tparams) 
    
  def EndProcessing(self, sfn, dfn):
    # Handles parameters: copyStat and preserveLastModified.
    Filter.EndProcessing(self, sfn, dfn)
    if dfn and os.path.exists(dfn):
      if self.copyStat:
        shutil.copystat(sfn, dfn)
      if self.preserveLastModified: 
        srcATime = os.path.getatime(sfn)
        srcMTime = os.path.getmtime(sfn)
        os.utime(sfn, (srcATime, srcMTime))

  def LogStartProcessing(self, sfn, dfn):
    self.Log(Dict.msgCopyingXToY % (sfn, dfn))
  
  def LogEnd(self):
    self.Log(Dict.msgCopiedAndSkipped % (self.processedFiles, self.skippedFiles), level = (LogLevel.INFO if not self.verbose else LogLevel.WARNING))
    