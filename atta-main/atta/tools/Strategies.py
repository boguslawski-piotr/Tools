'''.. no-user-reference:'''
import os
import hashlib
import OS

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
    v.patch = 0
  def NextMinor(self, v):
    v.minor += 1
    v.patch = 0
  def NextPatch(self, v):
    v.patch += 1
  def NextBuild(self, v):
    v.build += 1

class VersionResetBuildStrategy(VersionDefaultStrategy):
  '''This strategy works almost as :py:class:`.VersionDefaultStrategy`
     but resets the build number to zero after each change of 
     a minor or major version.
  '''
  def NextMajor(self, v):
    VersionDefaultStrategy.NextMajor(self, v)
    v.build = 0
  def NextMinor(self, v):
    VersionDefaultStrategy.NextMinor(self, v)
    v.build = 0
