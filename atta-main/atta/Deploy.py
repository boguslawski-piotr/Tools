"""TODO: description"""
import sys
from . import AttaError, Dict, OS

class Deployer:
  """TODO: description"""
  def Deploy(self, baseDirName, files, package, data, defaultRepository = None):
    """Returns list of all deployed files."""
    files = OS.Path.AsList(files)
    result = []
    for e in data:
      if isinstance(e, basestring):
        e = dict(repository = e)

      # Prepare repository module name.
      repositoryName = e.get(Dict.repository)
      if not repositoryName:
        if not defaultRepository:
          raise AttaError(self, Dict.errNotSpecified.format(Dict.repository))
        repositoryName = defaultRepository
      if not isinstance(repositoryName, basestring):
        repositoryName = repositoryName.__name__

      try:
        __import__(repositoryName)
        repository = sys.modules[repositoryName].Repository(e)
        result += repository.Put(files, baseDirName, package)
      finally:
        repository = None

    return result
