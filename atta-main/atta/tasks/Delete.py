""".. Files, directories: Deletes files or/and directories"""
import os

from ..tools.Misc import RemoveDuplicates
from .. import Dict, FileSet, DirSet, ExtendedFileSet, OS, LogLevel, Task

class Delete(Task):
  """
  Deletes files or/and directories.

  TODO: more...

  Parameters:

  * **srcs** |req| -               TODO Exactly the same as `srcs` in :py:class:`.ExtendedFileSet`
  * **force** |False| -            When set to `True` then the files with read-only attribute are also deleted.
  * **includeEmptyDirs** |False| - Whether to remove all empty directories from which files were deleted.
  * **failOnError**  |True| -      Controls whether an error stops the build or is only reported to the log.
  * **verbose** |False| -          Whether to show the name of each deleted file / directory.
  * **quiet** |False| -            Be extra quiet. No error is reported even with log level set to VERBOSE. Sets the `failOnError` to `False`.
  """
  def __init__(self, srcs, **tparams):
    self._delete(srcs, **tparams)

  def _delete(self, srcs, **tparams):
    #self._DumpParams(locals())

    # Parameters.
    self.force = tparams.get(Dict.paramForce, False)
    self.includeEmptyDirs = tparams.get('includeEmptyDirs', False)
    self.failOnError = tparams.get(Dict.paramFailOnError, True)
    self.verbose = tparams.get('verbose', False)
    self.quiet = tparams.get(Dict.paramQuiet, False)
    if self.quiet:
      self.failOnError = False

    # Prepare file names/directory names.
    if isinstance(srcs, FileSet):
      srcs = [srcs]
    filesSet = OS.Path.AsList(srcs)
    dirsSet = filter((lambda src:
                        isinstance(src, DirSet)
                        or (not isinstance(src, FileSet) and os.path.isdir(src))),
                      filesSet)
    filesSet = filter((lambda src: src not in dirsSet), filesSet)
    tmpDirsSet = []
    for dn in dirsSet:
      if isinstance(dn, DirSet): tmpDirsSet.extend(dn)
      else: tmpDirsSet.append(dn)
    dirsSet = RemoveDuplicates(tmpDirsSet)
    dirsSet.sort(reverse = True)

    self.filesDeleted = 0
    self.dirsDeleted = 0
    self.errors = 0

    # 1.
    # For each file:
    filesDirsSet = set()
    for r, f in ExtendedFileSet(filesSet):
      # Collect its directory (for third step - see below) and remove it.
      f = os.path.normpath(os.path.join(r, f))
      if os.path.isdir(f):
        self._delete(f, **tparams)
      else:
        filesDirsSet.add(os.path.dirname(f))
        err = OS.RemoveFile(f, self.force, self.failOnError)
        if err:
          self.errors += 1
          self.Log(Dict.errOSErrorForX % (err, os.strerror(err), f), level = LogLevel.ERROR)
        else:
          self.filesDeleted += 1
          self.Log(Dict.msgFile % f, level = (LogLevel.VERBOSE if not self.verbose else LogLevel.WARNING))

    def DelDirectories(dirs, ignore):
      for dn in dirs:
        if not dn: continue
        err = OS.RemoveDir(dn, False)
        if err and not err in ignore:
          if self.failOnError:
            raise OSError(err, os.strerror(err), dn)
          self.errors += 1
          self.Log(Dict.errOSErrorForX % (err, os.strerror(err), dn), level = LogLevel.ERROR)
        elif not err:
          self.dirsDeleted += 1
          self.Log(Dict.msgDirectory % dn, level = (LogLevel.VERBOSE if not self.verbose else LogLevel.WARNING))

    # 2.
    # For each directory:
    for dn in dirsSet:
      dn = os.path.normpath(dn)

      # Delete all files (with full control).
      for r, f in ExtendedFileSet(os.path.join(dn, '**/*')):
        f = os.path.normpath(os.path.join(r, f))
        err = OS.RemoveFile(f, self.force, self.failOnError)
        if err:
          self.errors += 1
          self.Log(Dict.errOSErrorForX % (err, os.strerror(err), f), level = LogLevel.ERROR)
        else:
          self.filesDeleted += 1
          self.Log(Dict.msgFile % f, level = (LogLevel.VERBOSE if not self.verbose else LogLevel.WARNING))

      # Delete all subdirectories.
      dd = DirSet(dn, '**/*', withRootDirName = True)
      dd.sort(reverse = True)
      DelDirectories(dd, [])

      # Delete appropriate directory.
      DelDirectories([dn], [])

    # 3.
    if self.includeEmptyDirs:
      # Remove all empty directories from which files were deleted in first step.
      filesDirsSet = list(filesDirsSet)
      filesDirsSet.sort(reverse = True)
      DelDirectories(filesDirsSet, [os.errno.ENOTEMPTY])

    if self.dirsDeleted or self.filesDeleted:
      self.Log(Dict.msgDeletedDirsAndFiles % (self.dirsDeleted, self.filesDeleted),
                 level = (LogLevel.INFO if not self.verbose else LogLevel.WARNING))

  def Log(self, msg = '', **args):
    if not self.quiet or self.LogLevel() == LogLevel.DEBUG:
      Task.Log(self, msg, **args)
