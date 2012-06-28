import os
import zipfile
from datetime import datetime, timedelta

from atta import Atta
from ..tasks.Base import Task
from ..tools.Misc import LogLevel
from ..tools.Sets import FileSet
from ..tasks.Javac import Javac
import atta.tools.OS as OS

class Jar(Task):
  '''
  .. snippet:: Jar
  
    .. code-block:: python

      Jar(fileName, srcs[, manifest, **tparams])}

    TODO: description

    :param string fileName: TODO
    :param srcs:            TODO
    :type srcs:             if string: file/dir/wildcard name or path (separator :) in which each item may be: file/dir/wildcard name
                            if list: each item may be: file/dir/wildcard name or FileSet
    :param manifest:        TODO
    :type manifest:         dict or string (fileName) or file-like object
    :param boolean checkCRC: TODO
    
  .. snippetref:: JavacUseCases
  
  ''' 
  def __init__(self, jarFileName, srcs, manifest = {}, **tparams):
    # get parameters
    if isinstance(srcs, basestring):
      srcs = srcs.split(':')
    checkCRC = tparams.get('checkCRC', True)

    if Atta.logger.GetLevel() == LogLevel.DEBUG:
      self.Log('\n*** Parameters:')
      self.LogIterable('srcs:', srcs)
      self.Log('checkCRC: {0}'.format(checkCRC))
      self.Log('')
    
    manifestFileName = 'META-INF/MANIFEST.MF' 
    manifestStr = self.ManifestAsStr(manifest, **tparams)
    jarFileName = os.path.normpath(jarFileName)
    changedFiles = []
    allFiles = []
    
    # collecting files to add
    self.Log('Checking: ' + jarFileName, level = LogLevel.VERBOSE)
    jar = None
    try:
      jar = zipfile.ZipFile(jarFileName, 'r')
    except:
      pass
    
    manifestChanged = False
    if jar != None:
      try:
        storedManifestStr = jar.read(manifestFileName)
        if manifestStr != storedManifestStr:
          manifestChanged = True
      except:
        manifestChanged = True
      
    for src in srcs:
      if len(src) <= 0:
        continue
      srcsSet = FileSet(createEmpty = True)
      rootDir = ''
      if isinstance(src, FileSet):
        rootDir = src.rootDir
        srcsSet = src
      else:
        if OS.Path.HasWildcards(src):
          rootDir, includes = OS.Path.Split(src)
          srcsSet.AddFiles(rootDir, includes = includes, realPaths = False)
        else:
          if os.path.isdir(src):
            rootDir = src
            srcsSet.AddFiles(rootDir, includes = '**/*', realPaths = False)
          else:
            rootDir, src = os.path.split(src)
            srcsSet = [src]
      
      for name in srcsSet:
        fullName = os.path.normpath(os.path.join(rootDir, name))
        changed = (jar == None)
        if not changed:
          try:
            info = jar.getinfo(os.path.normpath(name).replace('\\', '/'))
            fileInJarTime = datetime(info.date_time[0], info.date_time[1], info.date_time[2], info.date_time[3], info.date_time[4], info.date_time[5], 0)
            fileTime = datetime.fromtimestamp(os.path.getmtime(fullName))
            changed = abs(fileTime - fileInJarTime) > timedelta(seconds = 2)
            if not changed and checkCRC:
              if info.CRC != OS.FileCRCn(fullName):
                changed = True
          except:
            changed = True
        allFiles.append((fullName, name))
        if changed:
          changedFiles.append((fullName, name))
        
    if jar is not None:
      jar.close()
              
    # create jar file (if nedded)
    sometingWasWritten = False  
    if len(changedFiles) > 0 or manifestChanged:
      self.Log('Creating: ' + jarFileName, level = LogLevel.INFO)
      with zipfile.ZipFile(jarFileName, 'w', zipfile.ZIP_DEFLATED) as jar:
        # add files
        self.Log('with files:', level = LogLevel.VERBOSE)
        for fullName, name in allFiles:
          jar.write(fullName, name)
          sometingWasWritten = True
          self.Log('%s from: %s' % (name, fullName), level = LogLevel.VERBOSE)
        
        # add manifest
        self.Log('with manifest:\n%s' % manifestStr.rstrip(), level = LogLevel.VERBOSE)
        jar.writestr(manifestFileName, manifestStr)
      
    if not sometingWasWritten and (len(changedFiles) > 0 or manifestChanged):
      self.Log('To: %s none have been added.' % jarFileName, level = LogLevel.WARNING)
         
  def ManifestAsStr(self, manifest = {}, **tparams):
    '''TODO: description'''
    # TODO: obsluzyc gdy manifest: string (fileName), file-like object
    manifestStr = 'Manifest-Version: 1.0\nAtta-Version: %s %s\n' % (Atta.name, Atta.versionName)
    for name, value in manifest.items():
      manifestStr = manifestStr + '{0}: {1}\n'.format(name, value)
    return manifestStr
  