""".. TODO: TODO"""
import os
import tarfile

from .. import LogLevel, Dict, Task, OS, Delete
from .Exec import Exec
from .PyExec import PyExec

class NoVersionError(ImportError): pass
class VersionError(ImportError): pass

class PyInstall(Task):
  """
  TODO: description
  """
  def __init__(self, packages, **tparams):
    # Parameters
    packages = OS.Path.AsList(packages)

    for package in packages:
      # Check whether the package is not already installed.
      tryInstall = False
      importName = package.artifactId if not package.importName else package.importName
      try:
        try:
          m = __import__(importName.lower())
        except ImportError as E:
          if not importName.islower():
            #print '***', E
            m = __import__(importName)
          else:
            raise

        v = m.__dict__.get('__version__')
        if not v: v = m.__dict__.get('version')
        if not v: v = m.__dict__.get(m, 'Version')
        if not v:
          raise NoVersionError('Package: %s does not contain information about the version.' % package.artifactId)
        else:
          if str(v).strip().lower() == str(package.version).strip().lower():
            self.Log('Package: %s already installed.' % package.AsStrWithoutType(), level = LogLevel.VERBOSE)
          else:
            raise VersionError('Package: %s already installed in version: %s' % (package.artifactId, str(v)))

      except NoVersionError as E:
        print '@@@', E
        tryInstall = True
      except VersionError as E:
        print '+++', E
        tryInstall = True
      except ImportError as E:
        print '***', E
        tryInstall = True

      if tryInstall:
        # The package is not installed or has a different version than required.
        for fileName in OS.Path.AsList(package.fileNames):
          dirName = os.path.join(os.path.dirname(fileName), '.unpacked')
          installUsingDistUtils = False
          installUsingWinInstaller = False

          if OS.Path.Ext(fileName) == 'msi':
            installUsingWinInstaller = True
          elif tarfile.is_tarfile(fileName):
            tarfile.open(fileName, 'r').extractall(dirName)
            installUsingDistUtils = True

          # Try to install.
          if installUsingWinInstaller:
            Exec(fileName)
          elif installUsingDistUtils:
            packageDirName = os.path.join(dirName, OS.Path.RemoveExt(OS.Path.RemoveExt(os.path.basename(fileName))))
            setupFileName = os.path.join(packageDirName, 'setup.py')
            if not os.path.exists(setupFileName):
              raise RuntimeError('Package: %s does not include file: setup.py' % package.AsStrWithoutType())
            else:
              installSteps = 'install' if not package.installSteps else package.installSteps
              for step in OS.Path.AsList(installSteps, ','):
                #print dirName, setupFileName, step
                PyExec(setupFileName, [step], dirName = packageDirName, **tparams)

          Delete(dirName)
