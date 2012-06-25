'''
.. snippet:: OS

  TODO: description
'''
import sys
import os
import hashlib
import re

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

'''
Directories Tools
'''
    
def MakeDirs(path):
  '''
  Recursive directory creation function. The parameter `path` can be a string 
  or a list (or any iterable object type) whose individual elements are strings.
  For each item works like :py:func:`os.makedirs` but not throwing an exception 
  if the leaf directory already exists.
  '''
  if isinstance(path, basestring):
    paths = [path]
  else:
    paths = path
  for path in paths:  
    try:
      os.makedirs(path)
    except os.error as e:
      if e.errno != os.errno.EEXIST:
        raise

'''
File tools
'''
    
def Remove(fileName):
  '''Remove (delete) the file. Works like :py:func:`os.remove` but not throwing an exception if file not exists.'''
  try:
    os.remove(fileName)
  except os.error as e:
    if e.errno != os.errno.ENOENT:
      raise

global INAVLID_FILE_SIZE
INVALID_FILE_SIZE = -1
'''Constant meaning incorrect file size (usually this means an error while attempting to read file size).'''

def FileSize(fileName):
  '''Returns the file size or INAVLID_FILE_SIZE on any error.'''
  try:
    info = os.stat(fileName)
  except:
    return INVALID_FILE_SIZE
  return info.st_size

def FileHash(fileName, algo = hashlib.md5(), chunkSize = 128 * 64):
  '''
  Creates a hash of a file using the selected encryption algorithm.
  Returns file hash as a string (hexdigest) or None on error.
  More information about the available algorithms can be found in :py:mod:`hashlib`.
  '''
  try:
    with open(fileName,'rb') as f: 
      for chunk in iter(lambda: f.read(chunkSize), b''): 
        algo.update(chunk)
  except:
    return None
  return algo.hexdigest()

def FileCRC(fileName, chunkSize = 32768):
  '''
  Creates a CRC of a file.
  Returns CRC as a string or None on error.
  '''
  import zlib
  prev = 0
  try:
    with open(fileName,'rb') as f: 
      for chunk in iter(lambda: f.read(chunkSize), b''): 
        prev = zlib.crc32(chunk, prev)
  except:
    return None
  return "{:08x}".format(prev & 0xFFFFFFFF)
