'''.. Files, directories: Various other TODO: '''
import sys
import os
import hashlib
import re
import shutil
import platform
import stat
from datetime import datetime, timedelta
from time import sleep

'''
Common Tools
'''

def IsWindows():
  return platform.system() == 'Windows'

'''
Path Tools
'''

class Path:
  '''TODO: description'''
  @staticmethod
  def Ext(fileName, lowerCase = True):
    '''Returns the file name extension without . (dot) or empty string.'''
    if fileName.rfind('.') < 0:
      return ''
    fileNameSplited = fileName.split('.')
    ext = fileNameSplited[len(fileNameSplited) - 1]
    if lowerCase: ext = ext.lower()
    return ext

  @staticmethod
  def RemoveExt(fileName):
    '''Returns the file name without extension.'''
    d = fileName.rfind('.')
    s = fileName.rfind('/')
    if s < 0:
      s = fileName.rfind('\\')
    return fileName if d <= 0 or d < s else fileName[0:d];

  @staticmethod
  def JoinExt(fileName, ext):
    if not ext.startswith('.'):
      ext = '.' + ext
    return fileName + ext

  @staticmethod
  def HasWildcards(fileName):
    '''TODO: description'''
    return re.search('(\?|\*)+', fileName) != None

  @staticmethod
  def Split(path):
    '''TODO: description'''
    l, r = os.path.split(path)
    if l.endswith('**'):
      l = l[:-2]
      r = '**/' + r
    return l, r

  @staticmethod
  def NormUnix(path):
    path = os.path.normpath(path).replace('\\', '/')
    return path

  @staticmethod
  def AsList(paths, sep = ':'):
    '''TODO: description'''
    if paths == None:
      return []
    from .Misc import isiterable
    if isinstance(paths, basestring):
      if sep == ':' and IsWindows():
        # This is a very ugly solution, but effective.
        while True:
          m = re.search('[a-zA-Z]{1,1}(\\:)\\\\', paths)
          if m is not None:
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
  def FromList(paths):
    '''TODO: description'''
    from .Misc import isiterable
    if not isiterable(paths):
      return paths
    return os.pathsep.join(paths)

  @staticmethod
  def TempName(dir_, ext):
    '''TODO: description'''
    if len(ext) > 0 and not ext.startswith('.'):
      ext = '.' + ext
    for i in xrange(0, 100):
      dt = datetime.now()
      name = dt.strftime('%Y%m%d%H%S%f') + ext
      if not os.path.exists(os.path.join(dir_, name)):
        return name
      sleep(0.05)
    return ''

'''
Directories Tools
'''

def MakeDirs(paths):
  '''
  Recursive directory creation function. The parameter `paths` can be a string 
  or a list (or any iterable object type) whose individual elements are strings.
  For each item works like :py:func:`os.makedirs` but not throwing an exception 
  if the leaf directory already exists.
  '''
  for dir_ in Path.AsList(paths):
    try:
      os.makedirs(dir_)
    except os.error as e:
      if e.errno != os.errno.EEXIST:
        raise

def RemoveDir(path, failOnError = True):
  '''Removes the directory `path`. Works like :py:func:`os.rmdir`. 
     When `failOnError` is set to `True` is not throwing an exception if the directory not exists.
     When `failOnError` is set to `False` returns `0` when the directory has been removed/not exists
     or :py:data:`os.errno` when an error has occurred.'''
  try:
    os.rmdir(path)
  except os.error as e:
    if e.errno != os.errno.ENOENT:
      if failOnError: raise
      return e.errno
  return 0

def RemoveDirs(paths, failOnError = True):
  '''Removes directories recursively. The parameter `paths` can be a string 
     or a list (or any iterable object type) whose individual elements are strings.
     For each item works like :py:func:`os.removedirs`.
     When `failOnError` is set to `True` is not throwing an exception if the directory not exists.
     When `failOnError` is set to `False` returns `0` when the directory has been removed/not exists
     or :py:data:`os.errno` when an error has occurred.'''
  for dir_ in Path.AsList(paths):
    try:
      os.removedirs(dir_)
    except os.error as e:
      if e.errno != os.errno.ENOENT:
        if failOnError: raise
        return e.errno
  return 0

'''
File tools
'''

def Touch(fileName, createIfNotExists = True):
  '''Changes the time of the file `fileName` to 'now'. 
     If the file does not exists and `createIfNotExists` is set to `True` then creates an empty file.'''
  if os.path.exists(fileName):
    os.utime(fileName, None)
  elif createIfNotExists:
    with open(fileName, 'wb'):
      pass

def SetReadOnly(fileName, v):
  '''Sets (if `v` is True) or unsets (if `v` is False) read-only flag for file `fileName`.
     Not throwing an exception if the file not exists.'''
  if os.path.exists(fileName):
    st = os.stat(fileName)
    os.chmod(fileName, stat.S_IMODE(st.st_mode) | (stat.S_IWRITE if not v else stat.S_IREAD))

def RemoveFile(fileName, force = False, failOnError = True):
  '''Removes the file `fileName`. 
     When `force` is set to `True` then the file is removed, even when it is read-only.
     When `failOnError` is set to `True` is not throwing an exception if the file not exists.
     When `failOnError` is set to `False` returns `0` when the file has been removed/not exists
     or :py:data:`os.errno` when an error has occurred.'''
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
  '''Returns the file `fileName` size or INAVLID_FILE_SIZE on any error.'''
  try:
    info = os.stat(fileName)
  except:
    return INVALID_FILE_SIZE
  return info.st_size

def CopyFile(fileName, destName, force = False):
  '''Copies the file `fileName` to the file or directory `destName`.
     If `destName` is a directory, a file with the same basename as 
     `fileName` is created (or overwritten) in the directory specified.
     The parameter `force` allows overwrite files with read-only attribute.
     Uses :py:func:`shutil.copy2`.'''
  if force and not os.path.isdir(destName):
    SetReadOnly(destName, False)
  shutil.copy2(fileName, destName)

def CopyFileIfDiffrent(fileName, destName, useHash = False, force = False, granularity = 1):
  '''
  Copies the file `fileName` to the file or directory `destName`
  only if modification times or SHA1-hashs are different or `destName` not exists. 
  If `destName` is a directory, a file with the same basename as 
  `fileName` is created (or overwritten) in the directory specified.
  The parameter `force` allows overwrite files with read-only attribute.
  Uses :py:func:`shutil.copy2`.
  Returns True if file was copied.
  '''
  shouldCopy = True
  if os.path.exists(fileName):
    if os.path.isdir(destName):
      destName = os.path.join(destName, os.path.basename(fileName))
    if os.path.exists(destName):
      if useHash:
        srcHash = FileHash(fileName, hashlib.sha1())
        destHash = FileHash(destName, hashlib.sha1())
        shouldCopy = srcHash != destHash
      else:
        srcTime = datetime.fromtimestamp(os.path.getmtime(fileName))
        destTime = datetime.fromtimestamp(os.path.getmtime(destName))
        shouldCopy = abs((srcTime - destTime)) > timedelta(seconds = granularity)
  if shouldCopy:
    CopyFile(fileName, destName, force)
  return shouldCopy

def FileHash(fileName, algo = hashlib.sha1(), chunkSize = 128 * 64):
  '''
  Creates a hash of a file using the selected encryption algorithm.
  Returns file hash as a string (hexdigest) or None on error.
  More information about the available algorithms can be found in :py:mod:`hashlib`.
  '''
  try:
    with open(fileName, 'rb') as f:
      for chunk in iter(lambda: f.read(chunkSize), b''):
        algo.update(chunk)
  except:
    return None
  return algo.hexdigest()

def FileCRCn(fileName, chunkSize = 32768):
  '''
  Creates a CRC of a file.
  Returns CRC as a int (32bits) or None on error.
  '''
  import zlib
  prev = 0
  try:
    with open(fileName, 'rb') as f:
      for chunk in iter(lambda: f.read(chunkSize), b''):
        prev = zlib.crc32(chunk, prev)
  except:
    return None
  return prev & 0xFFFFFFFF

def FileCRC(fileName, chunkSize = 32768):
  '''
  Creates a CRC of a file.
  Returns CRC as a string or None on error.
  '''
  return "{:08x}".format(FileCRCn(fileName, chunkSize))
