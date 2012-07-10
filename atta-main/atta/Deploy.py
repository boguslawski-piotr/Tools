'''TODO: description'''
import sys

from .tools import OS
from . import Dict

class Deployer:
  '''TODO: description'''
  def Deploy(self, packageId, files, baseDirName, data):
    '''Returns list of all deployed files.'''
    files = OS.Path.AsList(files)
    result = []
    for e in data:
      repositoryName = e.get(Dict.repository)
      if repositoryName is None:
        continue
      try:
        __import__(repositoryName)
        repository = sys.modules[repositoryName].Repository(e)
        result += repository.Put(files, baseDirName, packageId)
      finally:
        repository = None

    return result
