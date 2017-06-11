""".. Java related: TODO: java"""
import os

from ..tools.Misc import isstring
from ..tools.ZipFile import ZipFile
from .. import Dict, LogLevel, Zip
from .. import Atta, AttaError

class Jar(Zip):
  """
    TODO: description

    Parameters:

    * **fileName** (string) TODO

    * **srcs**              TODO
      if string: file/dir/wildcard name or path (separator :) in which each item may be: file/dir/wildcard name
      if list: each item may be: file/dir/wildcard name or FileSet or DirSet
      also FileSet or DirSet alone

    * **manifest**          TODO (dict or string (fileName) or file-like object)

    * **checkCRC**          TODO

    Returns: TODO

    **Methods:**
  """
  def __init__(self, fileName, srcs, manifest = None, **tparams):
    #self._DumpParams(locals())

    # Parameters.
    manifestStr = self.ManifestAsStr(manifest, **tparams)
    fileName = os.path.normpath(fileName)

    manifestChanged = True
    try:
      with ZipFile(fileName, 'r') as zipFile:
        storedManifestStr = zipFile.read(Dict.manifestFileName)
        if manifestStr == storedManifestStr:
          manifestChanged = False
    except Exception:
      pass

    Zip.__init__(self, fileName, srcs, **tparams)

    if manifestChanged or self.sometingWasWritten:
      if not self.sometingWasWritten:
        self.Log(Dict.msgCreating.format(fileName), level = LogLevel.INFO)
      with ZipFile(fileName, 'a') as zipFile:
        # add manifest
        self.LogIterable(Dict.msgWithManifest, manifestStr.rstrip().split(Dict.newLine), level = LogLevel.VERBOSE)
        zipFile.writestr(Dict.manifestFileName, manifestStr)

  def ManifestAsStr(self, manifest = None, **tparams):
    """TODO: description"""
    manifestStr = Dict.basicManifest % (Atta.name, Atta.version)
    if manifest:
      if isstring(manifest):
        manifestStr += manifest
      elif 'read' in dir(manifest):
        manifestStr += manifest.read()
      elif isinstance(manifest, dict):
        for name, value in manifest.items():
          manifestStr += '%s: %s\n' % (name, value)
      else:
        raise AttaError(self, Dict.errInvalidParameterType % 'manifest')
    return manifestStr
