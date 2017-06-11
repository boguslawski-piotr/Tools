""".. TODO: TODO"""
import os
import sys
import re
import tarfile
import zipfile
from site import getsitepackages, getusersitepackages

from .. import AttaError, LogLevel, Dict, Task, OS, FileSet, DirFileSet, Delete, Version, PackageId
from ..Project import NeedsRestartError
from .Exec import Exec
from .PyExec import PyExec

class NoVersionError(ImportError): pass
class VersionError(ImportError): pass

class PyInstall(Task):
  """
  TODO: description
  you may specify:
   package:
    fileNames (req)
    importName (if not then artifactId)
    siParams (params for install, def: none)

  returns object with properties:

  installedPackages
  badPackages

  they are a lists which each element is 5ple:
    (package, importName, returnCode, errorMsg, output)

  """
  def __init__(self, packages, **tparams):
    # Parameters
    packages = OS.Path.AsList(packages)
    failOnError = tparams.get(Dict.paramFailOnError, True)
    force = tparams.get(Dict.paramForce, False)
    upgrade = tparams.get('upgrade', True)
    downgrade = tparams.get('downgrade', False)
    sgParams = OS.SplitCmdLine(tparams.get('sgParams', []))
    siParams = OS.SplitCmdLine(tparams.get('siParams', []))

    self.installedPackages = []
    self.badPackages = []
    needsRestart = False

    # Process all packages.
    for package in packages:
      importName = package.artifactId if not package.importName else package.importName
      tryInstall = False
      try:
        # Check whether the package is not already installed.
        module, importName = self.TryImport(importName)
        installedPackage = self.FindInPath(package)
        if installedPackage is not None:
          installedVersion = installedPackage.version
        else:
          installedVersion = self.FindVersion(module)

        # Check installed version and required version.
        if not installedVersion:
          msg = 'Error: Package: %s does not provide information about the version comprehensible to Python.' % package.AsStrWithoutTypeAndVersion()
          self.Log(msg, level = LogLevel.ERROR)
          if force:
            self.Log("Trying to install package: %s" % package.AsStrWithoutType(), level = LogLevel.INFO)
            tryInstall = True
        else:
          pv = Version.FromStr(package.version, fileName = None)
          iv = Version.FromStr(installedVersion, fileName = None)
          tryReinstall = False
          if pv == iv:
            self.Log('Package: %s already installed.' % package.AsStrWithoutType(), level = LogLevel.VERBOSE)
            if force:
              tryReinstall = True
          else:
            self.Log('Package: %s already installed in version: %s' % (package.AsStrWithoutTypeAndVersion(), str(installedVersion)),
                     level = LogLevel.INFO)
            if force:
              tryReinstall = True
            else:
              if pv > iv:
                if upgrade:
                  self.Log('Trying to upgrade to version: %s.' % str(package.version), level = LogLevel.INFO)
                  tryInstall = True
              else:
                if downgrade:
                  self.Log('Trying to downgrade to version: %s.' % str(package.version), level = LogLevel.INFO)
                  tryInstall = True

          if tryReinstall:
            self.Log("Trying to reinstall package: %s" % package.AsStrWithoutType(), level = LogLevel.INFO)
            tryInstall = True

      except ImportError:
        self.Log('Package: %s not installed. Trying to install.' % package.AsStrWithoutType(), level = LogLevel.INFO)
        tryInstall = True

      if tryInstall:
        # The package is not installed, has a different version
        # than required or parameter 'force' was specified.
        for fileName in OS.Path.AsList(package.fileNames):
          dirName = os.path.join(os.path.dirname(fileName), '.unpacked')
          installUsingDistUtils = False

          # Prepare files for installation.
          try:
            if tarfile.is_tarfile(fileName):
              tarfile.open(fileName, 'r').extractall(dirName)
              installUsingDistUtils = True
            elif zipfile.is_zipfile(fileName):
              zipfile.ZipFile(fileName, mode = 'r', allowZip64 = True).extractall(dirName)
              installUsingDistUtils = True
          except Exception as E:
            if failOnError:
              raise
            else:
              self.Log(Dict.FormatException(E), level = LogLevel.ERROR)
              continue

          # Try install.
          output = ''
          returnCode = 0
          installOK = False
          if installUsingDistUtils:
            files = FileSet(dirName, 'setup.py:*/setup.py', withRootDirName = True)
            if not files:
              msg = 'Package: %s does not contain file: setup.py' % package.AsStrWithoutType()
              if failOnError:
                raise AttaError(self, msg)
              else:
                self.Log(Dict.FormatException(msg), level = LogLevel.ERROR)
                continue
            else:
              for setupFileName in files:
                params  = sgParams[:]
                params += ['install']
                params += siParams if not package.siParams else OS.SplitCmdLine(package.siParams)
                e = PyExec(setupFileName, params, dirName = os.path.dirname(setupFileName), **tparams)
                output += e.output
                returnCode = e.returnCode
                installOK = returnCode == 0
                if not installOK:
                  break

          if not installOK:
            self.Log(Dict.FormatException('Package: %s NOT installed.' % (package.AsStrWithoutType())), level = LogLevel.ERROR)
            self.badPackages.append((package, importName, returnCode, '', output))
          else:
            # The package was probably fully installed. Now try to modify
            # the Python environment so that we can use installed package.
            self.RemoveFromPath(package)
            self.AddToPath(package)
            try:
              module, importName = self.TryImport(importName)
              reload(module)

              installedPackage = self.FindInPath(package)
              if installedPackage is None:
                installedVersion = self.FindVersion(module)
              else:
                installedVersion = installedPackage.version

              self.Log('Package: %s installed in version: %s'
                          % (package.AsStrWithoutTypeAndVersion(), str(installedVersion)), level = LogLevel.INFO)
              self.installedPackages.append((package, importName, returnCode, '', output))

            except ImportError as E:
              self.badPackages.append((package, importName, -1, str(E), output))
              needsRestart = True
            except Exception as E:
              if failOnError:
                raise
              else:
                self.Log(Dict.FormatException(E), level = LogLevel.ERROR)
                self.badPackages.append((package, importName, -1, str(E), output))

          # Delete temporary files and directories.
          Delete(dirName, quiet = True, force = True, failOnError = failOnError)

    if needsRestart:
      msg = 'The following packages reported problems during the import:\n\n'
      for package, importName, returnCode, errorMsg, output in self.badPackages:
        msg += '  %s (%s)\n  %s\n' % (package.AsStrWithoutType(), importName, Dict.FormatException(errorMsg))
      msg += "\nProbably were installed the packages of which Atta knows nothing.\nRestarting the build should fix the problem."
      if failOnError:
        raise NeedsRestartError(msg)
      else:
        self.Log(msg, level = LogLevel.ERROR)

  def TryImport(self, importName):
    importName = importName.replace('-', '.')
    names = [importName,
             importName.lower() if not importName.islower() else '',
             importName.capitalize() if not importName[0].isupper() else '',
             importName.replace('py', '') if 'py' in importName else '',
             importName.replace('py', '').capitalize() if 'py' in importName and not importName[0].isupper() else '',
            ]

    def _TryImport(name):
      try:
        module = __import__(name)
        return module, name
      except ImportError as E:
        return None, name

    module = None
    badNames = []
    for name in names:
      if name:
        module, name = _TryImport(name)
        if module:
          return module, name
        else:
          badNames.append(str(name))

    raise ImportError('No module(s) named: ' + ', '.join(badNames))

  def FindVersion(self, module):
    try:
      v = module.__dict__.get('__version__')
      if not v: v = module.__dict__.get('version')
      if not v: v = module.__dict__.get('_version')
      if not v: v = module.__dict__.get('Version')
      if not v: v = module.__dict__.get('_Version')
      if not v: v = module.__dict__.get('VERSION')
      if not v: v = module.__dict__.get('_VERSION')
      return v
    except Exception:
      return None

  def FindInPath(self, package):
    def _FindInPath(name, package):
      packageRegExp = re.compile(name + r'-([a-zA-Z0-9\._]+)-')

      for path in sys.path:
        m = packageRegExp.search(path)
        if m:
          return PackageId.FromPackage(package, version = m.group(1))

      sp = getsitepackages()
      sp.append(getusersitepackages())
      for path in sp:
        for fn in DirFileSet(path, packageRegExp, useRegExp = True):
          m = packageRegExp.search(fn)
          if m:
            return PackageId.FromPackage(package, version = m.group(1))

    p = _FindInPath(package.artifactId, package)
    if p is None:
      p = _FindInPath(package.artifactId.replace('-', '_'), package)
    return p

  def RemoveFromPath(self, package):
    def _RemoveFromPath(name, package):
      packageRegExp = re.compile(name + r'-([a-zA-Z0-9\._]+)-')
      newsyspath = []
      for path in sys.path:
        m = packageRegExp.search(path)
        if not m:
          newsyspath.append(path)
      sys.path = newsyspath

    _RemoveFromPath(package.artifactId, package)
    _RemoveFromPath(package.artifactId.replace('-', '_'), package)

  def AddToPath(self, package):
    # Find all 'site-packages' directories.
    sp = getsitepackages()
    sp.append(getusersitepackages())
    for path in sp:
      if path not in sys.path and os.path.exists(path):
        sys.path.append(path)

    # Add package to sys.path.
    def _AddToPath(name, version):
      for path in sp:
        packageFileName = name + '-' + version
        files = DirFileSet(path, [packageFileName + '*.egg', packageFileName + '*.zip'], withRootDirName = True)
        for fn in files:
          if fn not in sys.path and os.path.exists(fn):
            sys.path.append(fn)
    _AddToPath(package.artifactId, package.version)
    _AddToPath(package.artifactId.replace('-', '_'), package.version)

    # Try to add all the packages that are missing in
    # sys.path but are listed in: easy-install.pth.
    for path in sp:
      pth = os.path.join(path, 'easy-install.pth')
      try:
        pth = OS.LoadFile(pth)
        pth = pth.split('\n')
        for fn in pth:
          if not fn.startswith(('#', "import ", "import\t")):
            fn = os.path.realpath(os.path.join(path, fn))
            if fn not in sys.path and os.path.exists(fn):
              sys.path.append(fn)
      except Exception as E:
        #self.Log(str(E), level = LogLevel.VERBOSE)
        pass
