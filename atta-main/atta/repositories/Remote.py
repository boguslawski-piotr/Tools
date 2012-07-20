""".. no-user-reference:"""
import ftplib
import urllib2

from ..tools.internal.Misc import ObjectFromClass
from ..tools.Misc import RemoveDuplicates, NamedFileLike
from ..tools.Interfaces import AbstractMethod
from .. import AttaError, OS, Dict, LogLevel
from . import ArtifactNotFoundError
from . import Styles
from . import Local

class Repository(Local.Repository):
  """TODO: description"""

  def _Get(self, package, scope, store, resolvedPackages):
    # First, look into the store (cache) if the required files
    # (for package and its dependencies) are all up to date.
    filesInStore = store.Check(package, scope)
    problem = False
    if filesInStore is None:
      # If something is obsolete then check if all required files are available
      # in repository and download additional information about them (eg. stamp).
      # Check the store again if it makes sense.
      try:
        allFiles, baseDirName = self.CheckAndPrepareFilesForGet(package)
      except Exception as E:
        self.Log(str(E), level = LogLevel.ERROR)
        problem = True
      else:
        if package.stamp is not None:
          filesInStore = store.Check(package, scope)
        if filesInStore is None:
          # The store still says that something is missing or out of date.
          download = True
          filesInStore = []

          # Get the dependencies.
          packages = self.GetDependencies(package, scope)
          for p in packages or ():
            if not package.Excludes(p):
              if p not in resolvedPackages:
                resolvedPackages.append(p)
                filesInStore += self._Get(p, scope, store, resolvedPackages)
          if packages:
            # After downloading all the dependencies, check the store third time.
            # This is intended to minimize the amount of downloads.
            filesInStore2 = store.Check(package, scope)
            if filesInStore2:
              download = False
              filesInStore = filesInStore2

          if download:
            # Download all files and put them into the store.
            self.Log(Dict.msgSendingXToY % (package.AsStrWithoutType(), store._Name()), level = LogLevel.INFO)
            filesToDownload = []
            try:
              for fn in allFiles:
                filesToDownload.append(NamedFileLike(fn, self.GetFileLike(fn, LogLevel.VERBOSE)))
            except ftplib.Error, urllib2.URLError:
              problem = True
            except Exception as E:
              self.Log(Dict.errXWhileGettingY % (str(E), str(package)), level = LogLevel.ERROR)
              problem = True
            if not problem and filesToDownload:
              try:
                filesInStore += store.Put(baseDirName, filesToDownload, package)
              except Exception as E:
                self.Log(Dict.errXWhileSavingY % (str(E), str(package)), level = LogLevel.ERROR)
                problem = True

    # Check results.
    if not filesInStore or problem:
      if not package.optional:
        raise ArtifactNotFoundError(self, Dict.errFailedToAssembleX % str(package))
      else:
        filesInStore = []

    # Return package and its dependencies files.
    filesInStore = RemoveDuplicates(filesInStore)
    self.Log(Dict.msgReturns % OS.Path.FromList(filesInStore), level = LogLevel.DEBUG)
    return filesInStore

  @AbstractMethod
  def DefaultStore(self):
    assert False

  def Get(self, package, scope, store = None):
    """TODO: description"""
    '''returns: list of filesNames'''
    if store is None:
      store = self.DefaultStore()
    if store is None:
      raise AttaError(self, Dict.errNotSpecified.format(Dict.putIn))

    if package.fileNames:
      self._styleImpl = ObjectFromClass(Styles.OnlyFileName)

    store.SetOptionalAllowed(self.OptionalAllowed())
    return self._Get(package, scope, store, [])

