import os
from datetime import datetime, timedelta

from ..tools.internal.Misc import ObjectFromClass
from ..tools.Misc import LogLevel
from ..tools.Sets import FileSet
from ..tasks.Base import Task
import atta.tools.OS as OS
from atta import AttaError
  
class Archive(Task):
  def __init__(self, _class, fileName, srcs, **tparams):
    self._DumpParams(locals())
    
    _impl = ObjectFromClass(_class)
    
    srcs = OS.Path.AsList(srcs)
    recreate = tparams.get('recreate', False)
    checkCRC = tparams.get('checkCRC', True)

    fileName = os.path.normpath(fileName)
    changedFiles = []
    allFiles = []
    
    # collecting files to add
    self.Log('Checking: ' + fileName, level = LogLevel.VERBOSE)
    archive = None
    try:
      archive = _impl.GetClass()(fileName, 'r')
      if not archive.CanWrite():
        raise AttaError(self, 'TODO: ')
    except:
      pass
    
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
        changed = (archive == None) or recreate
        if not changed:
          try:
            inArchiveFileTime = archive.FileTime(name)
            fileTime = datetime.fromtimestamp(os.path.getmtime(fullName))
            changed = abs(fileTime - inArchiveFileTime) > timedelta(seconds = 2)
            if not changed and checkCRC and archive.HasCRCs():
              if archive.FileCRCn(name) != OS.FileCRCn(fullName):
                changed = True
          except:
            changed = True
        allFiles.append((fullName, name))
        if changed:
          changedFiles.append((fullName, name))
        
    if archive is not None:
      archive.close()
              
    # create archive file (if nedded)
    self.sometingWasWritten = False  
    if len(changedFiles) > 0 or recreate:
      self.Log('Creating: ' + fileName, level = LogLevel.INFO)
      with _impl.GetClass()(fileName, 'w') as archive:
        # add files
        self.Log('with files:', level = LogLevel.VERBOSE)
        for fullName, name in allFiles:
          archive.write(fullName, name)
          self.sometingWasWritten = True
          self.Log('  %s from: %s' % (name, fullName), level = LogLevel.VERBOSE)
        
    if not self.sometingWasWritten and (len(changedFiles) > 0 or recreate):
      self.Log('To: %s none have been added.' % fileName, level = LogLevel.WARNING)
