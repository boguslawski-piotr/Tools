'''.. Archive TODO: TODO'''
import os
from datetime import datetime, timedelta

from ..tools.internal.Misc import ObjectFromClass
from .. import AttaError, Dict, LogLevel, OS, FileSet, Task

class Archive(Task):
  '''TODO: description

    * **srcs**        TODO
      if string: file/dir/wildcard name or path (separator :) in which each item may be: file/dir/wildcard name
      if list: each item may be: file/dir/wildcard name or FileSet or DirSet
      also FileSet or DirSet alone
  
  '''
  def __init__(self, _class, fileName, srcs, **tparams):
    self._DumpParams(locals())

    _impl = ObjectFromClass(_class)

    if isinstance(srcs, FileSet):
      srcs = [srcs]
    srcs = OS.Path.AsList(srcs)
    recreate = tparams.get('recreate', False)
    checkCRC = tparams.get('checkCRC', True)

    fileName = os.path.normpath(fileName)
    changedFiles = []
    allFiles = []

    # collecting files to add
    self.Log(Dict.msgChecking.format(fileName), level = LogLevel.VERBOSE)
    archive = None
    try:
      archive = _impl.GetClass()(fileName, 'r')
      if not archive.CanWrite():
        raise AttaError(self, Dict.errArchiveImplCantWrite)
    except:
      pass

    for src in srcs:
      if len(src) <= 0:
        continue
      srcsSet = FileSet(createEmpty = True)
      rootDirName = ''
      # TODO: handle DirSet
      if isinstance(src, FileSet):
        rootDirName = src.rootDirName
        srcsSet = src
      else:
        if OS.Path.HasWildcards(src):
          rootDirName, includes = OS.Path.Split(src)
          srcsSet.AddFiles(rootDirName, includes = includes, realPaths = False, withRootDirName = False)
        else:
          if os.path.isdir(src):
            rootDirName = src
            srcsSet.AddFiles(rootDirName, includes = '**/*', realPaths = False, withRootDirName = False)
          else:
            rootDirName, src = os.path.split(src)
            srcsSet = [src]

      for name in srcsSet:
        fullName = os.path.normpath(os.path.join(rootDirName, name))
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
      self.Log(Dict.msgCreating.format(fileName), level = LogLevel.INFO)
      with _impl.GetClass()(fileName, 'w') as archive:
        # add files
        self.Log(Dict.msgWithFiles, level = LogLevel.VERBOSE)
        for fullName, name in allFiles:
          archive.write(fullName, name)
          self.sometingWasWritten = True
          self.Log('  ' + Dict.msgXfromY % (name, fullName), level = LogLevel.VERBOSE)

    if not self.sometingWasWritten and (len(changedFiles) > 0 or recreate):
      self.Log(Dict.msgNoneHaveBeenAdded % fileName, level = LogLevel.WARNING)
