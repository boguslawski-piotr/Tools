""".. Files, directories: Various other TODO: """
import os
import hashlib
import re
import shutil
import platform
import stat
from datetime import datetime, timedelta
from time import sleep

#
# Common Tools

def IsWindows():
  """Returns `True` if the code is executed in Windows."""
  return platform.system() == 'Windows'

def IsLinux():
  """Returns `True` if the code is executed in Linux (any version)."""
  return platform.system() in ('Linux',)

def IsOSX():
  """Returns `True` if the code is executed in Mac OSX (any version)."""
  return platform.system() == 'MacOS'

def IsUnix():
  """Returns `True` if the code is executed in Linux (any version)."""
  return IsLinux() or IsOSX()

#
# Path Tools

class Path:
  """TODO: description"""
  @staticmethod
  def Ext(fileName, lowerCase = True):
    """Returns the *fileName* extension without . (dot) or empty string."""
    if fileName.rfind('.') < 0:
      return ''
    fileNameSplited = fileName.split('.')
    ext = fileNameSplited[len(fileNameSplited) - 1]
    if lowerCase: ext = ext.lower()
    return ext

  @staticmethod
  def RemoveExt(fileName):
    """Returns the *fileName* without extension (the part after . (dot))."""
    d = fileName.rfind('.')
    s = fileName.rfind('/')
    if s < 0:
      s = fileName.rfind('\\')
    return fileName if d <= 0 or d < s else fileName[0:d]

  @staticmethod
  def JoinExt(fileName, ext):
    """TODO: description"""
    if not ext.startswith('.'):
      ext = '.' + ext
    return fileName + ext

  @staticmethod
  def HasWildcards(path):
    """Tests whether or not a *path* include wildcard characters (\?, \*)."""
    return re.search('(\?|\*)+', path) is not None

  @staticmethod
  def HasAntStyleWildcards(path):
    """Tests whether or not a *path* include Ant-style wildcard characters (\*\*)."""
    return path.find('**') >= 0

  @staticmethod
  def Match(pattern, path, useRegExp = False, fullMatch = True):
    """
    Tests whether or not a *path* matches against a *pattern*.
    The *path* is always converted to Unix style with ``/``
    as separator even on Windows.

    If *useRegExp* is true then matching is done using the regular
    expression compatible with :py:mod:`re` module.
    In the *pattern* you can pass the regular expression as a string
    or regular expression object.

    If *useRegExp* is `False` then this function is a implementation
    for Ant-style path patterns. The mapping matches paths using
    the following rules:

      **?**    -  matches one character,

      **\***   -  matches zero or more characters,

      **\*\*** -  matches zero or more 'directories' in a path

    Examples (borrowed from Ant):

      **\*\*/CVS/\*** - Matches all files in CVS directories that can be located anywhere in the directory tree.
      Matches::

        CVS/Repository
        org/apache/CVS/Entries
        org/apache/jakarta/tools/ant/CVS/Entries

      but not::

        org/apache/CVS/foo/bar/Entries (foo/bar/ part does not match)

      **org/atta/tests/\*\*** - Matches all files in the org/atta/tests directory tree.
      Matches::

        org/atta/tests/inc/inc2/something
        org/atta/tests/test.xml

      but not::

        org/atta/xyz.java (tests/ part is missing).

      **org/apache/\*\*/CVS/\*** - Matches all files in CVS directories that are located anywhere
      in the directory tree under org/apache. Matches::

        org/apache/CVS/Entries
        org/apache/jakarta/tools/ant/CVS/Entries

      but not::

        org/apache/CVS/foo/bar/Entries (foo/bar/ part does not match)

      **\*\*/test/\*\*** - Matches all files that have a test element in their path, including
      test as a filename. Matches::

        org/apache/test/CVS/Entries/a.a
        test/.a

      but not::

        org/apache/CVS/Entries/test.a
        test_move.py

      and so on.

    """
    path = path.replace('\\', '/')
    if useRegExp:
      if isinstance(pattern, basestring):
        return re.match(pattern, path) is not None
      else:
        return pattern.match(path) is not None

    #
    #  PathMatcher implementation for Ant-style path patterns.
    #  Based on the Java version found here:
    #
    #      http://www.docjar.com/html/api/org/springframework/util/AntPathMatcher.java.html
    #
    #  Copyright 2002-2012 the original author or authors.
    #
    #  Licensed under the Apache License, Version 2.0 (the "License");
    #  you may not use this file except in compliance with the License.
    #  You may obtain a copy of the License at
    #
    #      http://www.apache.org/licenses/LICENSE-2.0
    #
    #  Unless required by applicable law or agreed to in writing, software
    #  distributed under the License is distributed on an "AS IS" BASIS,
    #  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    #  See the License for the specific language governing permissions and
    #  limitations under the License.
    #
    #  Authors:
    #    Alef Arendsen, Juergen Hoeller, Rob Harrop, Arjen Poutsma, Piotr Boguslawski (porting to Python)
    #

    pattern = pattern.replace('\\', '/')
    if path.startswith('/') != pattern.startswith('/'):
      return False

    # Behavior compatible with Ant:
    # There is one "shorthand":
    # if a pattern ends with / or \, then ** is appended.
    if pattern.endswith('/'):
      pattern += '**'

    DOT = '\\.'
    ONE_CHAR = '.{1,1}'
    ANY_FILE_NAME_CHAR = '[^<>:"/\\|?*]' + '*'

    pattern = pattern.replace('.', DOT)
    pattern = pattern.replace('?', ONE_CHAR)

    def match(p, s):
      p = '^' + p.replace('*', ANY_FILE_NAME_CHAR) + '$'
      return re.match(p, s) is not None

    pattDirs = pattern.split('/')
    pathDirs = path.split('/')

    pattIdxStart = 0
    pattIdxEnd = len(pattDirs) - 1
    pathIdxStart = 0
    pathIdxEnd = len(pathDirs) - 1

    # Match all elements up to the first **
    while pattIdxStart <= pattIdxEnd and pathIdxStart <= pathIdxEnd:
      patDir = pattDirs[pattIdxStart]
      if '**' == patDir:
        break
      if not match(patDir, pathDirs[pathIdxStart]):
        return False
      pattIdxStart += 1
      pathIdxStart += 1

    if pathIdxStart > pathIdxEnd:
      # Path is exhausted, only match if rest of pattern is * or **'s
      if pattIdxStart > pattIdxEnd:
        return path.endswith('/') if pattern.endswith('/') else not path.endswith('/')
      if not fullMatch:
        return True
      if pattIdxStart == pattIdxEnd and '*' == pattDirs[pattIdxStart] and path.endswith('/'):
        return True
      for i in range(pattIdxStart, pattIdxEnd + 1):
        if not '**' == pattDirs[i]:
          return False
      return True
    elif pattIdxStart > pattIdxEnd:
      # String not exhausted, but pattern is. Failure.
      return False
    elif not fullMatch and '**' == pattDirs[pattIdxStart]:
      # Path start definitely matches due to "**" part in pattern.
      return True

    # up to last '**'
    while pattIdxStart <= pattIdxEnd and pathIdxStart <= pathIdxEnd:
      patDir = pattDirs[pattIdxEnd]
      if '**' == patDir:
        break
      if not match(patDir, pathDirs[pathIdxEnd]):
        return False
      pattIdxEnd -= 1
      pathIdxEnd -= 1
    if pathIdxStart > pathIdxEnd:
      # String is exhausted.
      for i in range(pattIdxStart, pattIdxEnd + 1):
        if not '**' == pattDirs[i]:
          return False
      return True

    while pattIdxStart != pattIdxEnd and pathIdxStart <= pathIdxEnd:
      patIdxTmp = -1
      for i in range(pattIdxStart + 1, pattIdxEnd + 1):
        if '**' == pattDirs[i]:
          patIdxTmp = i
          break
      if patIdxTmp == pattIdxStart + 1:
        ## '**/**' situation, so skip one
        pattIdxStart += 1
        continue

      # Find the pattern between padIdxStart & padIdxTmp in str between
      # strIdxStart & strIdxEnd
      patLength = (patIdxTmp - pattIdxStart - 1)
      strLength = (pathIdxEnd - pathIdxStart + 1)
      foundIdx = -1

      for i in range(0, strLength - patLength + 1):
        cont = False
        for j in range(0, patLength):
          subPat = pattDirs[pattIdxStart + j + 1]
          subStr = pathDirs[pathIdxStart + i + j]
          if not match(subPat, subStr):
            cont = True
            break
        if cont:
          continue
        foundIdx = pathIdxStart + i
        break

      if foundIdx == -1:
        return False

      pattIdxStart = patIdxTmp
      pathIdxStart = foundIdx + patLength

    for i in range(pattIdxStart, pattIdxEnd + 1):
      if not '**' == pattDirs[i]:
        return False

    return True

  @staticmethod
  def Split(path):
    """TODO: description"""
    l, r = os.path.split(path)
    if l.endswith('**'):
      l = l[:-2]
      r = '**/' + r
    return l, r

  @staticmethod
  def NormUnix(path):
    """TODO: description"""
    path = os.path.normpath(path).replace('\\', '/')
    return path

  @staticmethod
  def AsList(paths, sep = ':'):
    """TODO: description"""
    if paths is None:
      return []
    from .Misc import isiterable
    if isinstance(paths, basestring):
      if sep == ':' and IsWindows():
        # This is a very ugly solution, but works.
        r = re.compile('[a-zA-Z]{1,1}(\\:)\\\\')
        while True:
          m = r.search(paths)
          if m:
            paths = paths.replace(m.group(0), m.group(0).replace(':', '<'))
          else:
            break
        paths = paths.split(sep)
        for i, path in enumerate(paths):
          paths[i] = path.replace('<', ':')
      else:
        paths = paths.split(sep)
    elif not isiterable(paths):
      return [paths]
    return list(paths) # return copy

  @staticmethod
  def FromList(iterable):
    """TODO: description"""
    from .Misc import isiterable
    if not isiterable(iterable):
      return iterable
    return os.pathsep.join(iterable)

  @staticmethod
  def TempName(dirName, ext):
    """TODO: description"""
    if len(ext) > 0 and not ext.startswith('.'):
      ext = '.' + ext
    for i in xrange(0, 100):
      dt = datetime.now()
      name = os.path.join(dirName, dt.strftime('%Y%m%d%H%S%f') + ext)
      if not os.path.exists(name):
        return name
      sleep(0.05)
    return ''

#
# Common

def SplitCmdLine(line):
  """Splits the command line parameters *line* (with space as separator) into a list.
     Correctly handles the characters ' and ".
     If *line* is `None` returns empty list.
     If *line* is a iterable then do nothing and returns *line*.
     If *line* is not a string then returns *line* as list with one element.
     Throws `SyntaxError` if the characters ' and " do not match."""
  if line is None:
    return []
  from .Misc import isstring, isiterable
  if isstring(line):
    insideQuotes = False
    quote = None
    params = []
    i = 0
    while i < len(line):
      if not insideQuotes:
        if line[i] == '"' or line[i] == "'":
          insideQuotes = not insideQuotes
          quote = line[i]
      elif line[i] == quote:
        insideQuotes = not insideQuotes
      if not insideQuotes:
        if line[i] == ' ' or i == len(line) - 1:
          param = line[:i + 1].strip()
          if param:
            if param[0] in '\'"': param = param[1:]
            if param[-1] in '\'"': param = param[:-1]
            params.append(param)
          line = line[i + 1:]
          i = -1
      i += 1
    if insideQuotes:
      raise SyntaxError(line)
    return params
  elif not isiterable(line):
    return [line]
  return line

#
# Directories Tools

def MakeDirs(dirNames):
  """Recursive directory creation function. The parameter *dirNames* can be a string
     or a list (or any iterable object type) whose individual elements are strings.
     For each item works like :py:func:`os.makedirs` but not throwing an exception
     if the leaf directory already exists.
  """
  for dir_ in Path.AsList(dirNames):
    try:
      if dir_:
        os.makedirs(dir_)
    except os.error as e:
      if e.errno != os.errno.EEXIST:
        raise

def RemoveDir(dirName, failOnError = True):
  """Removes the directory *dirName*. Works like :py:func:`os.rmdir`.
     When *failOnError* is set to `True` is not throwing an exception if the directory not exists.
     When *failOnError* is set to `False` returns `0` when the directory has been removed/not exists
     or :py:data:`os.errno` when an error has occurred."""
  try:
    if dirName:
      os.rmdir(dirName)
  except os.error as e:
    if e.errno != os.errno.ENOENT:
      if failOnError: raise
      return e.errno
  return 0

def RemoveDirs(dirNames, failOnError = True):
  """Removes directories recursively. The parameter *dirNames* can be a string
     or a list (or any iterable object type) whose individual elements are strings.
     For each item works like :py:func:`os.removedirs`.
     When *failOnError* is set to `True` is not throwing an exception if the directory not exists.
     When *failOnError* is set to `False` returns `0` when the directory has been removed/not exists
     or :py:data:`os.errno` when an error has occurred."""
  for dn in Path.AsList(dirNames):
    try:
      if dn:
        os.removedirs(dn)
    except os.error as e:
      if e.errno != os.errno.ENOENT:
        if failOnError: raise
        return e.errno
  return 0

#
# File tools

def Touch(fileName, createIfNotExists = True):
  """Changes the time of the file *fileName* to 'now'.
     If the file does not exists and *createIfNotExists*
     is set to `True` then creates an empty file."""
  if os.path.exists(fileName):
    os.utime(fileName, None)
  elif createIfNotExists:
    with open(fileName, 'wb'):
      pass

def IsReadOnly(fileName):
  """Checks if the file *fileName* is read-only."""
  if os.path.exists(fileName):
    st = os.stat(fileName)
    return stat.S_IMODE(st.st_mode) & (stat.S_IREAD | stat.S_IWRITE) != (stat.S_IREAD | stat.S_IWRITE)
  return False

def SetReadOnly(fileName, v):
  """Sets (if *v* is `True`) or unsets (if *v* is `False`) read-only flag for file *fileName*.
     Not throwing an exception if the file not exists."""
  if os.path.exists(fileName):
    st = os.stat(fileName)
    if not v:
      os.chmod(fileName, stat.S_IMODE(st.st_mode) | stat.S_IWRITE)
    else:
      os.chmod(fileName, (stat.S_IMODE(st.st_mode) & ~stat.S_IWRITE) | stat.S_IREAD)

def RemoveFile(fileName, force = False, failOnError = True):
  """Removes the file *fileName*.
     When *force* is set to `True` then the file is removed, even when it is read-only.
     When *failOnError* is set to `True` is not throwing an exception if the file not exists.
     When *failOnError* is set to `False` returns `0` when the file has been removed/not exists
     or :py:data:`os.errno` when an error has occurred."""
  # TODO: if error retry once
  try:
    if force:
      SetReadOnly(fileName, False)
    os.remove(fileName)
  except os.error as e:
    if e.errno != os.errno.ENOENT:
      if failOnError: raise
      return e.errno
  return 0

global INAVLID_FILE_SIZE
INVALID_FILE_SIZE = -1
'''Constant meaning incorrect file size (usually this means an error while attempting to read file size).'''

def FileSize(fileName):
  """Returns the file *fileName* size or INAVLID_FILE_SIZE on any error."""
  try:
    info = os.stat(fileName)
  except Exception:
    return INVALID_FILE_SIZE
  return info.st_size

def CopyFile(fileName, dest, force = False):
  """Copies the file *fileName* to the file or directory *dest*.
     If *dest* is a directory, a file with the same basename as
     *fileName* is created (or overwritten) in the directory specified.
     The parameter *force* allows overwrite files with read-only attribute.
     Uses :py:func:`shutil.copy2`."""
  if force and not os.path.isdir(dest):
    SetReadOnly(dest, False)
  shutil.copy2(fileName, dest)

def CopyFileIfDiffrent(fileName, dest, useHash = False, force = False, granularity = 1):
  """Copies the file *fileName* to the file or directory *dest*
     only if modification times or SHA1-hashs are different or *dest* not exists.
     If *dest* is a directory, a file with the same basename as
     *fileName* is created (or overwritten) in the directory specified.
     The parameter *force* allows overwrite files with read-only attribute.
     Uses :py:func:`shutil.copy2`.
     Returns True if file was copied.
  """
  shouldCopy = True
  if os.path.exists(fileName):
    if os.path.isdir(dest):
      dest = os.path.join(dest, os.path.basename(fileName))
    if os.path.exists(dest):
      if useHash:
        srcHash = FileHash(fileName, hashlib.sha1())
        destHash = FileHash(dest, hashlib.sha1())
        shouldCopy = srcHash != destHash
      else:
        srcTime = datetime.fromtimestamp(os.path.getmtime(fileName))
        destTime = datetime.fromtimestamp(os.path.getmtime(dest))
        shouldCopy = abs((srcTime - destTime)) > timedelta(seconds = granularity)
  if shouldCopy:
    CopyFile(fileName, dest, force)
  return shouldCopy

def FileTimestamp(fileName):
  """Creates timestamp for file *fileName*."""
  return os.path.getmtime(fileName)

def FileHash(fileName, algo, chunkSize = 128 * 64):
  """Creates a hash of the file *fileName* using the selected encryption algorithm.
     Returns file hash as a string (hexdigest) or `None` on error.
     More information about the available algorithms can be found in :py:mod:`hashlib`.
  """
  try:
    with open(fileName, 'rb') as f:
      for chunk in iter(lambda: f.read(chunkSize), b''):
        algo.update(chunk)
  except Exception:
    return None
  return algo.hexdigest()

def FileCRCn(fileName, chunkSize = 32768):
  """Creates a CRC of the file *fileName*.
     Returns CRC as a int (32bits) or `None` on error.
  """
  import zlib
  prev = 0
  try:
    with open(fileName, 'rb') as f:
      for chunk in iter(lambda: f.read(chunkSize), b''):
        prev = zlib.crc32(chunk, prev)
  except Exception:
    return None
  return prev & 0xFFFFFFFF

def FileCRC(fileName, chunkSize = 32768):
  """Creates a CRC of the file *fileName*.
     Returns CRC as a string or `None` on error.
  """
  return "{:08x}".format(FileCRCn(fileName, chunkSize))

def LoadFile(fileName, binary = False):
  """Loads file *fileName* into memory buffer."""
  f = open(fileName, 'r' + ('b' if binary else ''))
  try:
    rc = f.read()
  finally:
    f.close()
  return rc
