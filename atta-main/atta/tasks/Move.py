'''.. Files, directories: Moves files: move'''
import os

from ..tools.Misc import LogLevel
from ..tools import OS
from .. import Dict
from .Copy import Copy

class Move(Copy):
  '''
  TODO: description
  Uses Copy task. Not Rename!
  Parameters from Filter and Copy.
  '''
  def __init__(self, srcs, dest, **tparams):
    # 'Move' files (copy + delete which is done in the function: self.EndProcessing)
    self.dirsToDelete = set()
    Copy.__init__(self, srcs, dest, **tparams)
    
    # Do not delete 'root' directories from file set.
    self.dirsDeleted = set()
    for rn, _ in self.srcs:
      self.dirsDeleted.add(os.path.normpath(rn))
    
    # Delete empty directories.
    self.dirsToDelete = list(self.dirsToDelete)
    self.dirsToDelete.sort(reverse = True)
    for d in self.dirsToDelete:
      d = os.path.normpath(d) 
      if not d in self.dirsDeleted:
        try: 
          os.rmdir(d)
          self.dirsDeleted.add(d)
          self.Log(Dict.msgDelDirectory % (d))
        except os.error as E: 
          if E.errno != os.errno.ENOTEMPTY and E.errno != os.errno.ENOENT: 
            self.HandleError(E, d)
      head, tail = os.path.split(d)
      if not tail:
        head, tail = os.path.split(head)
      while head and tail:
        try:
          if not head in self.dirsDeleted:
            os.rmdir(head)
            self.dirsDeleted.add(head)
            self.Log(Dict.msgDelDirectory % (head))
        except os.error:
          break
        head, tail = os.path.split(head)
    
  def EndProcessing(self, sfn, dfn):
    Copy.EndProcessing(self, sfn, dfn)
    OS.RemoveFile(sfn, self.force)
    self.dirsToDelete.add(os.path.dirname(sfn))

#  def LogStartProcessing(self, sfn, dfn):
#    self.Log(Dict.msgMovingXToY % (sfn, dfn))
  
  def LogEnd(self):
    if self.processedFiles or self.skippedFiles:
      self.Log(Dict.msgMovedAndSkipped % (self.processedFiles, self.skippedFiles), 
                 level = (LogLevel.INFO if not self.verbose else LogLevel.WARNING))
