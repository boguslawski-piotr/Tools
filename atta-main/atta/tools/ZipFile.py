""".. Archives: zip TODO"""
import os
import zipfile
from datetime import datetime

from .Interfaces import IArchiveFile
from .. import AttaError

class ZipFile(IArchiveFile):
  def __init__(self, fileName, mode, password = None, **tparams):
    self.zip = zipfile.ZipFile(fileName, mode, zipfile.ZIP_DEFLATED, allowZip64 = True)
    if password is not None:
      self.zip.setpassword(password)

  def close(self):
    self.zip.close()

  def CanWrite(self):
    return True

  def write(self, file_, arcName):
    if isinstance(file_, basestring):
      return self.zip.write(file_, arcName)
    else:
      raise AttaError(self, 'TODO: Not implemented.')

  def writestr(self, data, arcName):
    return self.zip.writestr(data, arcName)

  def CanRead(self):
    return True

  def read(self, fileName, password = None):
    return self.zip.read(fileName, password)

  def FileTime(self, fileName):
    info = self.zip.getinfo(os.path.normpath(fileName).replace('\\', '/'))
    return datetime(info.date_time[0], info.date_time[1], info.date_time[2], info.date_time[3], info.date_time[4], info.date_time[5], 0)

  def HasCRCs(self):
    return True

  def FileCRCn(self, fileName):
    return self.zip.getinfo(os.path.normpath(fileName).replace('\\', '/')).CRC

  def FileCRC(self, fileName):
    return "{:08x}".format(self.FileCRCn(fileName))

  def __enter__(self):
    return self

  def __exit__(self, type, value, traceback):
    self.zip.close()
    return False
