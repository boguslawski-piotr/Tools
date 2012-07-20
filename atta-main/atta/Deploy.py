"""TODO: description"""
import sys

from .tools.internal.Misc import AttaClassOrModule
from .tools.Misc import isstring
from .repositories import Base
from . import AttaError, LogLevel, Dict, OS, Task

class Deployer(Task):
  """TODO: description"""
  def Deploy(self, baseDirName, files, package, data, defaultRepository = None):
    """Returns list of all deployed files."""
    files = OS.Path.AsList(files)
    failOnError = True
    result = []
    for e in data:
      try:
        if isstring(e): e = dict(repository = e)
        failOnError = e.get(Dict.paramFailOnError, True)

        # Prepare repository object.
        # You can provide: instance, class, module, module name
        repositoryName = e.get(Dict.repository)
        if not repositoryName:
          if not defaultRepository:
            raise AttaError(self, Dict.errNotSpecified.format(Dict.repository))
          repositoryName = defaultRepository
        if Base.Repository.IsMyInstance(repositoryName):
          repository = repositoryName
        elif Base.Repository.IsMySubclass(repositoryName):
          repository = repositoryName(**e)
        else:
          if not isstring(repositoryName):
            repositoryName = repositoryName.__name__
          repositoryName = AttaClassOrModule(repositoryName)
          __import__(repositoryName)
          repository = sys.modules[repositoryName].Repository(**e)

        # Put files into repository.
        result += repository.Put(baseDirName, files, package)

      except Exception as E:
        if failOnError:
          raise
        else:
          self.Log(str(E), level = LogLevel.ERROR)

    return result
