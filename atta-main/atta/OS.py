import os
import hashlib

global INAVLID_FILE_SIZE
INVALID_FILE_SIZE = -1

## Returns the file name extension or empty string.
#  \ingroup Utils 
def Ext(fileName):
  if fileName.rfind('.') < 0:
    return ''
  fileNameSplited = fileName.split('.')
  return fileNameSplited[len(fileNameSplited) - 1].lower()

## Removes the extension from the file name.
#  \return New file name without extension.
#  \ingroup Utils 
def RemoveExt(fileName):
  i = fileName.rfind('.')
  return fileName if i <= 0 else fileName[0:i];
  
## Works like os.remove but not throwing an exception if path not exists.
#  \ingroup Utils 
def Remove(path):
  try:
    os.remove(path)
  except os.error as e:
    if e.errno != os.errno.ENOENT:
      raise

## Works like os.makedirs but not throwing an exception if path exists.
#  \ingroup Utils 
def MakeDirs(path):
  try:
    os.makedirs(path)
  except os.error as e:
    if e.errno != os.errno.EEXIST:
      raise

## Gets the file size.
#  \return the file size or INAVLID_FILE_SIZE on any error.
#  \ingroup Utils 
def FileSize(fileName):
  try:
    info = os.stat(fileName)
  except:
    return INVALID_FILE_SIZE
  return info.st_size

## Creates a hash of a file using the selected encryption algorithm.
#  More information about the available algorithms can be found 
#  <a href="http://docs.python.org/library/hashlib.html">here.</a>
#  \return File hash as a string (hexdigest) or None on error.
#  \ingroup Utils 
def FileHash(fileName, algo = hashlib.md5(), chunkSize = 128 * 64):
  try:
    with open(fileName,'rb') as f: 
      for chunk in iter(lambda: f.read(chunkSize), b''): 
        algo.update(chunk)
  except:
    return None
  return algo.hexdigest()

## Creates a CRC of a file.
#  \return CRC as a string or None on error.
#  \ingroup Utils 
def FileCRC(fileName, chunkSize = 32768):
  import zlib
  prev = 0
  try:
    with open(fileName,'rb') as f: 
      for chunk in iter(lambda: f.read(chunkSize), b''): 
        prev = zlib.crc32(chunk, prev)
  except:
    return None
  return "{:08x}".format(prev & 0xFFFFFFFF)
