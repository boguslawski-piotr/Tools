import os
import zipfile

from atta import Atta
from ..tasks.Base import Task
from ..tools.Misc import LogLevel
from ..tools.Sets import FileSet
import atta.tools.OS as OS

class Jar(Task):
  '''
  .. snippet:: Jar
  
    .. code-block:: python

      Jar(fileName, srcs[, manifest, **tparams])}

    TODO: description

    :param string fileName: TODO
    :param srcs:            TODO
    :type srcs:             string, string path or list of strings
    :param dict manifest:   TODO
    
  .. snippetref:: JavacUseCases
  
  ''' 
  def __init__(self, fileName, srcs, manifest = {}, **tparams):
    # get parameters
    if isinstance(srcs, basestring):
      srcs = srcs.split(':')
    
    # create jar
    self.Log('Creating jar: ' + os.path.realpath(fileName))
    with zipfile.ZipFile(fileName, 'w') as jar:
      # create and add manifest
      manifestStr = 'Manifest-Version: 1.0\n'
      for name, value in manifest.items():
        manifestStr = manifestStr + '{0}: {1}\n'.format(name, value)
      jar.writestr('META-INF/MANIFEST.MF', manifestStr)
      self.Log('with manifest:\n%s' % manifestStr.rstrip(), level = LogLevel.VERBOSE)
      
      # add files
      self.Log('and files:', level = LogLevel.VERBOSE)
      for src in srcs:
        if len(src) <= 0:
          continue
        
        srcsSet = FileSet(createEmpty = True)
        rootDir = ''
        if OS.Path.HasWildcards(src):
          rootDir, includes = OS.Path.Split(src)
          srcsSet.AddFiles(rootDir, includes = includes, realPaths = False)
        else:
          if os.path.isdir(src):
            rootDir = src
            srcsSet.AddFiles(src, includes = '**/*.class', realPaths = False)
          else:
            rootDir, src = os.path.split(src)
            srcsSet = [src]
        
        for fileName in srcsSet:
          fullFileName = os.path.realpath(os.path.join(rootDir, fileName))
          jar.write(fullFileName, fileName)
          if Atta.logger.GetLevel() <= LogLevel.VERBOSE:
            fullFileName = fullFileName.replace(fileName, '')
            self.Log('%s from: %s' % (fileName, fullFileName), level = LogLevel.VERBOSE)

      