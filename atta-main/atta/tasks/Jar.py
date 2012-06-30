'''.. Java related: TODO: java'''
import os

from ..tools.ZipFile import ZipFile
from ..tasks.Zip import Zip
from ..tools.Misc import LogLevel
from atta import Atta

class Jar(Zip):
  '''
    TODO: description

    Parameters:
    
    * **fileName** (string) TODO
    
    * **srcs**              TODO 
      if string: file/dir/wildcard name or path (separator :) in which each item may be: file/dir/wildcard name
      if list: each item may be: file/dir/wildcard name or FileSet
    
    * **manifest**          TODO (dict or string (fileName) or file-like object)

    * **checkCRC**          TODO
    
    Returns: TODO
    
    **Methods:**
  ''' 
  def __init__(self, fileName, srcs, manifest = {}, **tparams):
    self._DumpParams(locals())
    
    manifestFileName = 'META-INF/MANIFEST.MF' 
    manifestStr = self.ManifestAsStr(manifest, **tparams)
    fileName = os.path.normpath(fileName)
    
    manifestChanged = True
    try:
      with ZipFile(fileName, 'r') as zipFile:
        storedManifestStr = zipFile.read(manifestFileName)
        if manifestStr == storedManifestStr:
          manifestChanged = False
    except:
      pass
              
    Zip.__init__(self, fileName, srcs, **tparams)
    
    if manifestChanged or self.sometingWasWritten:
      if not self.sometingWasWritten:
        self.Log('Creating: ' + fileName, level = LogLevel.INFO)
      with ZipFile(fileName, 'a') as zipFile:
        # add manifest
        self.LogIterable('with manifest:', manifestStr.rstrip().split('\n'), level = LogLevel.VERBOSE)
        zipFile.writestr(manifestFileName, manifestStr)
         
  def ManifestAsStr(self, manifest = {}, **tparams):
    '''TODO: description'''
    # TODO: obsluzyc gdy manifest: string (fileName), file-like object
    manifestStr = 'Manifest-Version: 1.0\nAtta-Version: %s %s\n' % (Atta.name, Atta.versionName)
    for name, value in manifest.items():
      manifestStr = manifestStr + '{0}: {1}\n'.format(name, value)
    return manifestStr
  