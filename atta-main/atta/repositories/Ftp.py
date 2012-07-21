""".. Remote: TODO"""
import ftplib
import os
import hashlib
import tempfile
from time import sleep

from ..loggers import Progress
from .. import AttaError, OS, Dict, LogLevel
from . import Base, Local, Remote

class Repository(Remote.Repository):
  """TODO: description"""
  def __init__(self, **tparams):
    Remote.Repository.__init__(self, **tparams)

    self.host = self.data.get(Dict.host)
    if not self.host:
      raise AttaError(self, Dict.errNotSpecified.format(Dict.host))
    if not self.rootDirName:
      raise AttaError(self, Dict.errNotSpecified.format(Dict.rootDirName))

    self.ftp = ftplib.FTP()
    self.ftp.set_debuglevel(0)

    self.port = self.data.get(Dict.port, 21)
    self.ftp.connect(self.host, self.port, self.data.get(Dict.timeout, Remote.DEFAULT_TIMEOUT))

    user = self.data.get(Dict.user)
    passwd = self.data.get(Dict.pasword)
    self.ftp.login(user, passwd)

    self.ftp.set_pasv(self.data.get(Dict.passive, False))

    self.cache = None
    if self.data.get(Dict.useCache, True):
      # NOTE: Cache is on the local file system.
      cacheDirName = os.path.normpath(os.path.join(os.path.expanduser('~'), Dict.attaExt, Dict.repository))
      self.cache = Local.Repository(style = self.data.get(Dict.style, Base.Repository.GetDefaultStyleImpl()),
                                    rootDirName = cacheDirName)

    self.maxRetries = self.data.get(Dict.maxRetries, 3)

  def __del__(self):
    try:
      if self.ftp:
        self.ftp.close()
    except Exception:
      pass
    finally:
      self.ftp = None

  def NormPath(self, path):
    return OS.Path.NormUnix(path)

  def MakeDirs(self, dirName):
    try:
      self.ftp.mkd(self.NormPath(dirName))
    except ftplib.error_perm as E:
      if str(E).find('550') >= 0:
        pass
      else:
        raise

  def FileSize(self, fileName):
    try:
      fileSize = self.ftp.size(self.NormPath(fileName))
    except ftplib.error_perm as E:
      if str(E).find('550') >= 0:
        return OS.INVALID_FILE_SIZE
      else:
        raise
    return fileSize if fileSize is not None else OS.INVALID_FILE_SIZE

  def FileExists(self, fileName):
    return self.FileSize(fileName) != OS.INVALID_FILE_SIZE

  def FileTime(self, fileName):
    # TODO: implement?
    return None

  def FileHash(self, fileName):
    # Without the implementation for performance reasons.
    # To calculate the hash you need to download a file from the server.
    return None

  def Touch(self, fileName):
    # TODO: I don't known method for simulate touch on ftp server :(
    pass

  def _GetFileLikeCallback(self, data):
    self.tempFile.write(data)
    self.progress.Feed(len(data))

  def GetFileLike(self, fileName, logLevel = LogLevel.VERBOSE):
    fileName = self.NormPath(fileName)
    self.Log(Dict.msgDownloading % self.Url() + fileName, level = logLevel)

    self.tempFile = tempfile.SpooledTemporaryFile(max_size = 1024 * 1024 * 5)
    retries = 0
    while retries < self.maxRetries:
      try:
        self.progress = Progress.Bar(max = self.FileSize(fileName))
        self.ftp.retrbinary('RETR ' + fileName, self._GetFileLikeCallback)
        self.tempFile.seek(0)
        self.progress.End()
        return self.tempFile
      except ftplib.Error as E:
        self.Log("Error '%s' while downloading: %s" % (str(E), self.Url() + fileName), level = LogLevel.ERROR)
        if str(E).find('550') >= 0:
          raise
        else:
          self.Log('Retry download (%d).' % (retries + 1), level = LogLevel.WARNING)
          self.tempFile.truncate()
          retries += 1
          if retries >= self.maxRetries:
            raise
          sleep(2.00)

  def _FileNameInCache(self, fileName):
    return os.path.join(str(self.cache.rootDirName), os.path.relpath(fileName, self.rootDirName))

  def GetFileContents(self, fileName, logLevel = LogLevel.DEBUG):
    if self.cache:
      # NOTE: We assume that the cache is a repository on the file system.
      # See also the notes in self.__init__().
      try:
        return self.cache.GetFileContents(self._FileNameInCache(fileName), logLevel)
      except Exception:
        pass

    f = self.GetFileLike(fileName, logLevel)
    try:
      rc = f.read()
    finally:
      f.close()
    return rc

  def _PutFileLikeCallback(self, data):
    self.sha1.update(data)
    if self.fileInCache:
      self.fileInCache.write(data)
    self.progress.Feed(len(data))

  def PutFileLike(self, f, fileName, logLevel = LogLevel.VERBOSE):
    self.fileInCache = None
    if self.cache:
      # NOTE: We assume that the cache is a repository on the file system.
      # See also the notes in self.__init__().
      fileNameInCache = self._FileNameInCache(fileName)
      OS.MakeDirs(os.path.dirname(fileNameInCache))
      self.fileInCache = open(fileNameInCache, 'wb')

    fileName = self.NormPath(fileName)
    self.Log(Dict.msgSaving % self.Url() + fileName, level = logLevel)

    bytesToSave = 0
    startPos = 0
    if 'tell' in dir(f):
      startPos = f.tell()
      f.seek(0, os.SEEK_END)
      bytesToSave = f.tell() - startPos
      f.seek(startPos)

    retries = 0
    while retries < self.maxRetries:
      try:
        self.progress = Progress.Bar('Saved', bytesToSave)
        self.sha1 = hashlib.sha1()
        self.ftp.storbinary('STOR ' + fileName, f, callback = self._PutFileLikeCallback) #, blocksize, callback, rest
        self.progress.End()
        break
      except ftplib.Error as E:
        self.Log("Error '%s' while saving: %s" % (str(E), self.Url() + fileName), level = LogLevel.ERROR)
        self.Log('Retry saving (%d).' % (retries + 1), level = LogLevel.WARNING)
        f.seek(startPos)
        if self.fileInCache:
          self.fileInCache.seek(0)
        retries += 1
        if retries >= self.maxRetries:
          raise
        sleep(1.00)

    sha1 = self.sha1.hexdigest()
    self.sha1 = None

    if self.fileInCache:
      try: self.fileInCache.close()
      finally: self.fileInCache = None

    return sha1

  def PutFile(self, srcFileName, destFileName, logLevel = LogLevel.VERBOSE):
    self.MakeDirs(os.path.dirname(destFileName))
    f = open(srcFileName, 'rb')
    try:
      rc = self.PutFileLike(f, destFileName, logLevel)
    finally:
      f.close()
    return rc

  def PutFileContents(self, contents, fileName, logLevel = LogLevel.DEBUG):
    f = tempfile.SpooledTemporaryFile(max_size = 1024 * 1024)
    f.write(contents)
    f.seek(0)
    self.PutFileLike(f, fileName, logLevel)

  def Url(self):
    return 'ftp://' + self.host + ':' + str(self.port) + '/'

  def CompleteFileName(self, fileName):
    return fileName

  def DefaultStore(self):
    return self.cache

  def _ChangeFileNamesToFtpUrls(self, fileNames):
    if fileNames:
      for i in range(len(fileNames)):
        fileNames[i] = self.Url() + self.NormPath(fileNames[i])
    return fileNames

  def Check(self, package, scope):
    if self.cache:
      # Check the local cache if exists.
      return self.cache.Check(package, scope)
    else:
      # Check the files on ftp.
      result = Local.Repository.Check(self, package, scope)
      if not result:
        return None
      return self._ChangeFileNamesToFtpUrls(result)

  def Put(self, fBaseDirName, files, package):
    # Put the files on ftp at the same time creating an exact copy in the local cache
    # (if the repository use cache, see also: PutFileLike method).
    result = Local.Repository.Put(self, fBaseDirName, files, package)
    if result and self.cache:
      # Because the cache had just been updated, we give local file names.
      for i in range(len(result)):
        result[i] = self._FileNameInCache(result[i])
      return result

    # If the repository is set to not use cache we give the full urls.
    return self._ChangeFileNamesToFtpUrls(result)

  def _Name(self):
#    name = Task._Name(self)
#    return 'Ftp.' + name
    return 'Ftp'
