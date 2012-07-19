""".. no-user-reference:"""
import os
import hashlib

from ..tools import OS
from .Interfaces import IRequiresCompileStrategy

class SrcNewerStrategy(IRequiresCompileStrategy):
  """TODO: description"""
  def RequiresCompile(self, srcFileName, destFileName, **tparams):
    """Returns `True` if `srcFileName` is newer than `destFileName`."""
    if not os.path.exists(srcFileName):
      return False
    if not os.path.exists(destFileName):
      return True
    destTime = os.path.getmtime(destFileName)
    srcTime = os.path.getmtime(srcFileName)
    return srcTime > destTime

  def Start(self, destDirName, **tparams): pass
  def End(self, **tparams): return []

class SrcHashStrategy(IRequiresCompileStrategy):
  """TODO: description"""
  def RequiresCompile(self, srcFileName, destFileName, **tparams):
    """Returns `True` if SHA1-hash of `srcFileName` is not equal to the last saved."""
    if not os.path.exists(srcFileName):
      return False

    srcHashFileName = os.path.join('.atta/srchash', os.path.dirname(srcFileName))
    if not os.path.exists(srcHashFileName):
      OS.MakeDirs(srcHashFileName)
    srcHashFileName = os.path.join(srcHashFileName, OS.Path.JoinExt(os.path.basename(srcFileName), 'sha1'))
    realSrcFileName = srcFileName

    srcHash = OS.FileHash(realSrcFileName, hashlib.sha1())
    storedSrcHash = None
    if os.path.exists(srcHashFileName):
      try:
        with open(srcHashFileName, 'rb') as f:
          storedSrcHash = f.read()
      except Exception:
        pass

    actionNeeded = False
    if srcHash != storedSrcHash:
      actionNeeded = True
      try:
        with open(srcHashFileName, 'wb') as f:
          f.write(srcHash)
      except Exception:
        pass

    if not os.path.exists(destFileName):
      actionNeeded = True

    return actionNeeded

  def Start(self, destDirName, **tparams): pass
  def End(self, **tparams): return []
