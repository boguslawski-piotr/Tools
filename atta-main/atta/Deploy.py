"""TODO: description"""
import sys

from .tools.internal.Misc import AttaClassOrModule
from .tools.Misc import isstring
from . import AttaError, Dict, OS

class Deployer:
  """TODO: description"""
  def Deploy(self, baseDirName, files, package, data, defaultRepository = None):
    """Returns list of all deployed files."""
    files = OS.Path.AsList(files)
    result = []

    for e in data:
      if isstring(e):
        e = dict(repository = e)

      # Prepare repository module name.
      repositoryName = e.get(Dict.repository)
      if not repositoryName:
        if not defaultRepository:
          raise AttaError(self, Dict.errNotSpecified.format(Dict.repository))
        repositoryName = defaultRepository
      if not isstring(repositoryName):
        repositoryName = repositoryName.__name__
      repositoryName = AttaClassOrModule(repositoryName)

      __import__(repositoryName)
      repository = sys.modules[repositoryName].Repository(e)
      result += repository.Put(baseDirName, files, package)

    return result
