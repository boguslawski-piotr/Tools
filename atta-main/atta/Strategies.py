import os
import hashlib

from tools.Interfaces import ICompareStrategy
import tools.OS as OS

class SrcNewerStrategy(ICompareStrategy):
  '''TODO: description'''
  def ActionNeeded(self, srcFileName, destFileName):
    '''Returns True if `srcFileName` is newer than `destFileName`.'''
    if not os.path.exists(srcFileName):
      return False
    if not os.path.exists(destFileName):
      return True
    destTime = os.path.getmtime(destFileName)
    srcTime = os.path.getmtime(srcFileName)
    if srcTime > destTime:
      return True
    return False

class SrcHashStrategy(ICompareStrategy):
  '''TODO: description'''
  def ActionNeeded(self, srcFileName, destFileName):
    '''Returns True if SHA1-hash of `srcFileName` is not equal to the last saved.'''
    if not os.path.exists(srcFileName):  
      return False
    srcHashFileName = os.path.join('.atta/markers', os.path.dirname(srcFileName))
    if not os.path.exists(srcHashFileName):
      OS.MakeDirs(srcHashFileName)
    srcHashFileName = os.path.join(srcHashFileName, os.path.basename(srcFileName))
    realSrcFileName = srcFileName

    srcHash = OS.FileHash(realSrcFileName, hashlib.sha1())
    storedSrcHash = None
    if os.path.exists(srcHashFileName):
      try:
        with open(srcHashFileName, 'rb') as f:
          storedSrcHash = f.read()
      except:
        pass
      
    actionNeeded = False
    if srcHash != storedSrcHash:
      actionNeeded = True
      try:
        with open(srcHashFileName, 'wb') as f:
          f.write(srcHash)
      except:
        pass
    
    if not os.path.exists(destFileName): 
      actionNeeded =  True
  
    return actionNeeded
  