'''.. no-user-reference:'''
import os
import hashlib
import OS

from .Interfaces import ICompareStrategy

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
    return srcTime > destTime

class SrcHashStrategy(ICompareStrategy):
  '''TODO: description'''
  def ActionNeeded(self, srcFileName, destFileName):
    '''Returns True if SHA1-hash of `srcFileName` is not equal to the last saved.'''
    if not os.path.exists(srcFileName):
      return False

    srcHashFileName = os.path.join('.atta/srchash', os.path.dirname(srcFileName))
    if not os.path.exists(srcHashFileName):
      OS.MakeDirs(srcHashFileName)
    srcHashFileName = os.path.join(srcHashFileName, os.path.basename(srcFileName) + '.sha1')
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
      actionNeeded = True

    return actionNeeded

#------------------------------------------------------------------------------ 

from Interfaces import IVersionStrategy

class VersionDefaultStrategy(IVersionStrategy):
  '''Default version strategy partially based on: http://semver.org/.
     When a major version number is incremented, the minor version and 
     patch version MUST be reset to zero. When a minor version number 
     is incremented, the patch version MUST be reset to zero. 
     For instance: 1.1.3 -> 2.0.0 and 2.1.7 -> 2.2.0.
  '''
  def NextMajor(self, v):
    v.major += 1
    v.minor = 0
    v.path = 0
  def NextMinor(self, v):
    v.minor += 1
    v.path = 0
  def NextPath(self, v):
    v.patch += 1
  def NextBuild(self, v):
    v.build += 1

class VersionResetBuildStrategy(VersionDefaultStrategy):
  '''This strategy works almost as :py:class:`.VersionDefaultStrategy`
     but resets the build number to zero after each change of a minor or major version.
  '''
  def NextMajor(self, v):
    VersionDefaultStrategy.NextMajor(self, v)
    v.build = 0
  def NextMinor(self, v):
    VersionDefaultStrategy.NextMinor(self, v)
    v.build = 0
