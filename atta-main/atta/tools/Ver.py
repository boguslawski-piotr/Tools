""".. Miscellaneous: Project version management: ver"""
import os
import re
import cStringIO

from .internal.Misc import ObjectFromClass
from .DefaultVarsExpander import Expander
from .Interfaces import Observable
from ..tasks.Base import Task
from .. import LogLevel, Dict, OS

class Version(Observable, Task):
  """TODO: description

  Parameters:

  * **fileName** `(version.info)`
  * **format**
  * **prefix** |None|
  * **postfix** |None|

  * **createIfNotExists** |True|
  * **quiet** |False|
  * **observers** |None|
  * **impl**

  """
  def __init__(self, **conf):
    self.Configure(**conf)

  class Formats:
    """TODO: description"""
    M = '${major}'
    Mp = '${major}${postfix}'
    MM = '${major}.${minor}'
    MMp = '${major}.${minor}${postfix}'
    MMP = '${major}.${minor}.${patch}'
    MMPp = '${major}.${minor}.${patch}${postfix}'
    MMPB = '${major}.${minor}.${patch}.${build}'
    MMPBp = '${major}.${minor}.${patch}.${build}${postfix}'

  class Events:
    """TODO: description"""
    NextMajor = 1
    NextMinor = 2
    NextPatch = 3
    NextBuild = 4
    SetPrefix = 5
    SetPostfix = 6
    AfterRead = 7
    BeforeUpdate = 8
    AfterUpdate = 9
    AfterConfigure = 10

  class IStrategy:
    """TODO: description"""
    def NextMajor(self, v):
      """TODO: description"""
      pass
    def NextMinor(self, v):
      """TODO: description"""
      pass
    def NextPath(self, v):
      """TODO: description"""
      pass
    def NextBuild(self, v):
      """TODO: description"""
      pass

  class DefaultStrategy(IStrategy):
    """Default version strategy partially based on: http://semver.org/.
       When a major version number is incremented, the minor version and
       patch version MUST be reset to zero. When a minor version number
       is incremented, the patch version MUST be reset to zero.
       For instance: 1.1.3 -> 2.0.0 and 2.1.7 -> 2.2.0.
    """
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

  class ResetBuildStrategy(DefaultStrategy):
    """This strategy works almost as :py:class:`.VersionDefaultStrategy`
       but resets the build number to zero after each change of
       a minor or major version.
    """
    def NextMajor(self, v):
      Version.DefaultStrategy.NextMajor(self, v)
      v.build = 0
    def NextMinor(self, v):
      Version.DefaultStrategy.NextMinor(self, v)
      v.build = 0

  def Configure(self, **conf):
    """TODO: description"""
    self._impl = ObjectFromClass(conf.get('impl', Version.GetDefaultImpl()))
    observers = OS.Path.AsList(conf.get('observers', None))
    for c in observers:
      self.AddObserver(c)

    self.major = 0
    self.minor = 0
    self.patch = 0
    self.build = 0
    self.changed = False

    self.quiet = conf.get(Dict.paramQuiet, False)
    self.format = conf.get('format', Version.Formats.MMPB)
    self.prefix = conf.get('prefix', '')
    self.postfix = conf.get('postfix', '')
    self.fileName = conf.get('fileName', 'version.info')
    if not self._Read():
      if conf.get('createIfNotExists', True):
        self._ForceUpdate()

    self.NotifyObservers(Version.Events.AfterConfigure)

  @staticmethod
  def FromStr(vstr, **tparams):
    v = Version(**tparams)
    vstr = [c if c.isdigit() else '.' + c if c != '.' else '.' for c in vstr]
    vstr = ''.join(vstr)
    vlist = vstr.split('.')
    def _int(s):
      # Change all not numeric chars to int.
      s = [c if c.isdigit() else str((ord(c.lower())-97)) if c.isalpha() else '0' for c in s]
      s = ''.join(s)
      return int(s)
    try:
      v.major = _int(vlist[0])
      v.minor = _int(vlist[1])
      v.patch = _int(vlist[2])
      v.build = _int(vlist[3])
    except Exception:
      pass
    return v

  def AsStr(self):
    """TODO: description"""
    return str(self)

  def NextMajor(self, update = True):
    """TODO: description"""
    old = self._AsStr()
    self._impl.GetObject().NextMajor(self)
    self.NotifyObservers(Version.Events.NextMajor)
    self._Changed(update, old)

  def NextMinor(self, update = True):
    """TODO: description"""
    old = self._AsStr()
    self._impl.GetObject().NextMinor(self)
    self.NotifyObservers(Version.Events.NextMinor)
    self._Changed(update, old)

  def NextPatch(self, update = True):
    """TODO: description"""
    old = self._AsStr()
    self._impl.GetObject().NextPatch(self)
    self.NotifyObservers(Version.Events.NextPatch)
    self._Changed(update, old)

  def NextBuild(self, update = True):
    """TODO: description"""
    old = self._AsStr()
    self._impl.GetObject().NextBuild(self)
    self.NotifyObservers(Version.Events.NextBuild)
    self._Changed(update, old)

  def SetPrefix(self, prefix):
    """TODO: description"""
    old = self.prefix
    self.prefix = prefix
    self.NotifyObservers(Version.Events.SetPrefix)
    return old

  def SetPostfix(self, postfix):
    """TODO: description"""
    old = self.postfix
    self.postfix = postfix
    self.NotifyObservers(Version.Events.SetPostfix)
    return old

  def ExpandVars(self, data, **tparams):
    """TODO: description"""
    e = Expander()
    return e.Expand(data,
                    major = self.major,
                    minor = self.minor,
                    patch = self.patch,
                    build = self.build,
                    prefix = self.prefix,
                    postfix = self.postfix,
                    version = str(self),
                    **tparams)

  _defaultImpl = ObjectFromClass(DefaultStrategy)

  @staticmethod
  def SetDefaultImpl(_class):
    """TODO: description"""
    Version._defaultImpl = ObjectFromClass(_class)

  @staticmethod
  def GetDefaultImpl():
    """TODO: description"""
    return Version._defaultImpl.GetClass()

  # private section

  def __del__(self):
    self._Update()

  def __str__(self):
    e = Expander()
    return e.Expand(self.format,
                    major = self.major,
                    minor = self.minor,
                    patch = self.patch,
                    build = self.build,
                    prefix = self.prefix,
                    postfix = self.postfix)


  def __eq__(self, other):
    return self._AsInt() == other._AsInt()
  def __ne__(self, other):
    return self._AsInt() != other._AsInt()
  def __lt__(self, other):
    return self._AsInt() < other._AsInt()
  def __le__(self, other):
    return self._AsInt() <= other._AsInt()
  def __gt__(self, other):
    return self._AsInt() > other._AsInt()
  def __ge__(self, other):
    return self._AsInt() >= other._AsInt()

  def _Changed(self, forceUpdate, old = None):
    if forceUpdate:
      self._ForceUpdate()
      if old:
        if not self.quiet:
          self.Log(Dict.msgChangedFromXToYInZ % (old, self._AsStr(), self.fileName), level = LogLevel.INFO)
    else:
      self.changed = True

  def _CreateIfNotExists(self):
    if self.fileName:
      if not os.path.exists(self.fileName):
        self._ForceUpdate()

  def _ForceUpdate(self):
    self.changed = True
    self._Update()

  def _Pattern(self):
    return re.compile('(\s*version_(\w+)\s*=\s*(\d+))\s*$')
  def _Pattern2(self):
    return re.compile('(\s*version\s*=\s*(.+))\s*$')

  def _Read(self):
    if not self.fileName:
      return True
    if not os.path.exists(self.fileName):
      return False
    f = open(self.fileName, 'r')
    try:
      pattern = self._Pattern()
      for line in f:
        m = pattern.search(line)
        if m:
          setattr(self, m.group(2), int(m.group(3)))
    finally:
      f.close()
    self.changed = False
    self.NotifyObservers(Version.Events.AfterRead)
    return True

  def _CreateNew(self):
    fo = cStringIO.StringIO()
    fo.write('\nversion_major = %d' % self.major)
    fo.write('\nversion_minor = %d' % self.minor)
    fo.write('\nversion_patch = %d' % self.patch)
    fo.write('\nversion_build = %d' % self.build)
    fo.write('\nversion = %s\n' % str(self))
    fo.seek(0)
    return fo

  def _UpdateExisting(self):
    if not self.fileName:
      return None
    found = False
    fo = cStringIO.StringIO()
    f = open(self.fileName, 'r')
    try:
      pattern = self._Pattern()
      pattern2 = self._Pattern2()
      for line in f:
        m = pattern.search(line)
        if m:
          n = m.group(1).replace(m.group(3), str(getattr(self, m.group(2))))
          line = line.replace(m.group(1), n)
          found = True
        else:
          m = pattern2.search(line)
          if m:
            n = m.group(1).replace(m.group(2), str(self))
            line = line.replace(m.group(1), n)
        fo.write(line)
    finally:
      f.close()
    if not found:
      fo.write(self._CreateNew().read())
    fo.seek(0)
    return fo

  def _Update(self):
    if not self.changed or not self.fileName:
      return True
    self.NotifyObservers(Version.Events.BeforeUpdate)

    if os.path.exists(self.fileName):
      fo = self._UpdateExisting()
    else:
      fo = self._CreateNew()
    f = open(self.fileName, 'wb')
    try:
      for line in fo:
        f.write(line)
    finally:
      f.close()
      fo.close()

    self.changed = False
    self.NotifyObservers(Version.Events.AfterUpdate)
    return True

  def _AsInt(self):
    return self.major * 100000000 + self.minor * 1000000 + self.patch * 5000 + self.build

  def _AsStr(self):
    return '%d.%d.%d.%d' % (self.major, self.minor, self.patch, self.build)

  def _FromStr(self, v):
    self.major, self.minor, self.patch, self.build = v.split('.')
