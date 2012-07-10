'''.. Files, directories: Deletes files or/and directories'''
import os

from ..tools.Misc import LogLevel
from ..tools.Sets import FileSet, DirSet, ExtendedFileSet
from ..tools import OS
from .. import Dict
from .Base import Task

class Delete(Task):
  '''
  Deletes files or/and directories.
  
  TODO: more...
  
  Parameters:
  
  * **srcs** -                     TODO Exactly the same as `srcs` in :py:class:`.ExtendedFileSet`
  * **force** |False| -            When set to `True` then the files with read-only attribute are also deleted.
  * **failOnError**  |True| -      Controls whether an error stops the build or is only reported to the log. Merely relevant if `quiet` is `False`.
  * **verbose** |False| -          Whether to show the name of each deleted file / directory.
  * **quiet** |False| -            Be extra quiet. No error is reported even with log level set to VERBOSE.
  * **includeEmptyDirs** |False| - Whether to remove all empty directories from which files were deleted.
  '''
  def __init__(self, srcs, force = False, **tparams):
    self._delete(srcs, force, **tparams)

  def _delete(self, srcs, force = False, **tparams):
    self._DumpParams(locals())

    failOnError = tparams.get('failOnError', True)
    verbose = tparams.get('verbose', False)
    quiet = tparams.get('quiet', False)
    if quiet:
      failOnError = False
    includeEmptyDirs = tparams.get('includeEmptyDirs', False)

    filesSet = OS.Path.AsList(srcs)
    dirsSet = filter((lambda src:
                        isinstance(src, DirSet)
                        or (not isinstance(src, FileSet) and os.path.isdir(src))),
                      filesSet)
    dirsSet = list(set(dirsSet))
    dirsSet.sort()
    dirsSet.reverse()
    filesSet = filter((lambda src: src if src not in dirsSet else None), filesSet)

    # 1.
    # For each file:
    filesDirsSet = set()
    for r, f in ExtendedFileSet(filesSet):
      # Collect its directory (for third step - see below) and remove it.
      f = os.path.normpath(os.path.join(r, f))
      filesDirsSet.add(os.path.dirname(f))
      if os.path.isdir(f):
        self._delete(f, force, **tparams)
      else:
        err = OS.RemoveFile(f, force, failOnError)
        if not quiet or self.LogLevel() == LogLevel.DEBUG:
          if err != 0:
            self.Log(Dict.errOSErrorForX % (err, os.strerror(err), f), level = LogLevel.WARNING)
          else:
            self.Log(Dict.msgFile % f, level = (LogLevel.VERBOSE if not verbose else LogLevel.WARNING))

    # 2.
    # For each directory:
    for d in dirsSet:
      d = os.path.normpath(d)

      # Delete all files (with full control).
      for r, f in ExtendedFileSet(os.path.join(d, '**/*')):
        f = os.path.normpath(os.path.join(r, f))
        err = OS.RemoveFile(f, force, failOnError)
        if err != 0 and (not quiet or self.LogLevel() == LogLevel.DEBUG):
          self.Log(Dict.errOSErrorForX % (err, os.strerror(err), f), level = LogLevel.WARNING)

      # Delete all subdirectories.
      dd = DirSet(d, '**/*')
      dd.sort()
      dd.reverse()
      err = OS.RemoveDirs(dd, failOnError)
      if not quiet or self.LogLevel() == LogLevel.DEBUG:
        if err != 0:
          self.Log(Dict.errOSErrorForX % (err, os.strerror(err), d), level = LogLevel.WARNING)
        else:
          self.Log(Dict.msgDirectory % d, level = (LogLevel.VERBOSE if not verbose else LogLevel.WARNING))

    # 3.
    if includeEmptyDirs:
      # Remove all empty directories from which files were deleted in first step.
      filesDirsSet = list(filesDirsSet)
      filesDirsSet.sort()
      filesDirsSet.reverse()
      for d in filesDirsSet:
        err = OS.RemoveDirs(d, False)
        if not quiet and err != 0 and err != os.errno.ENOTEMPTY:
          if failOnError:
            raise OSError(err, os.strerror(err), d)
          self.Log(Dict.errOSErrorForX % (err, os.strerror(err), d), level = LogLevel.WARNING)
