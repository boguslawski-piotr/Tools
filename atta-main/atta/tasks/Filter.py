""".. Data manipulation: TODO: filter, filter2"""
import os
import tempfile

from .. import Dict, LogLevel, OS, ExtendedFileSet, Task
from .. import AttaError

class Filter(Task):
  """
  TODO: description

  Parameters:

  * **srcs** |req| -                     TODO Exactly the same as `srcs` in :py:class:`.ExtendedFileSet`
    TODO: allow file like object(s)

  * **destDirName** |None| - directory

  or

  * **destFile** |None| - file name or file like object

  Parameters related to *dest...* only:

  * **append** |True| - for existing file or file like object. If False then the file is truncated.
  * **failIfDestNotExists** |False| - for dir or file name
  * **failIfDestExists** |False| - For `dest` if it's a file name or directory.

  Parameters related to source files and created destination files:

  * **failIfExists** |False| - For created files if *destDirName*.
    TODO: change name (?)

  * **force** |False| -            When set to `True` then the files with read-only attribute are overriden.
    For `dest` if it's a file name or for created files if `dest` is a directory.

  * **fileNameTransforms** |None| - one or more (list) callables implements IFileNameTransform
    Valid only if *destDirName* specyfied.

    .. code-block:: python

      def IFileNameTransform(srcRootDirName, srcFileName,
                               destDirName, actualDestFileName, **tparams)

    Must return valid file name or `None` if you want to use the `actualDestFileName`.
    The `tparams` has a entry named `caller`, which is a reference to the object that triggered the transformation.

  * **fileFilters** |None| - one or more (list) callables implements IFileFilter, first False stops further checking (if list)
    Ten filtr moze sluzyc do eliminowania przetwarzania dla niektorych plikow.
    Np. w Copy z ustawionym: kopiuj tylko gdy nowsze.
    Itp. itd.

    .. code-block:: python

      def IFileFilter(srcFileName, destFileName, **tparams):

    Must return True if src is meant to be further processed.
    If returns False then file is skipped.
    `destFileName` may be `None`.
    The `tparams` has a entry named `caller`, which is a reference to the object that triggered the filter.

  * **dataFilters** |None| - one or more (list) callable implements IDataFilter or instance of class that implements IDataFilter

    .. code-block:: python

      class IDataFilter:
        def Start(self, srcFileName, destFileName, **tparams):
          # return ignored (yet)
          # src is not open
          # dest may not exists
          # optional

        def __call__(self, data, **tparams):
          # data operations
          # optional
          return data

        def End(self, **tparams):
          # return ignored (yet)
          # src is closed
          # dest should exists and it's closed
          # optional

    or

    .. code-block:: python

      def IDataFilter(data, **tparams):
        # data operations
        return data

    The `tparams` has a entry named `caller`, which is a reference to the object that triggered the filter.

  * **srcBinaryMode** - |False|
  * **destBinaryMode** - |False|
  * **binaryMode** - |False|
  * **chunkSize** - 32768 for src, if srcBinaryMode/binaryMode is True

  * **failOnError** |True| -      Controls whether an error stops the build or is only reported to the log.
  * **verbose** |False|-          Whether to show the name of each processed file.
  * **quiet** |False| -           Be extra quiet. No error is reported even with log level set to VERBOSE. Sets the `failOnError` to `False`.

  """
  def __init__(self, srcs, **tparams):
    self.verbose = False
    self._DumpParams(locals())

    # Parameters.
    if 'binaryMode' in tparams:
      binaryMode = ('b' if tparams.get('binaryMode', False) else '')
      self.srcBinaryMode = binaryMode
      self.destBinaryMode = binaryMode
    else:
      self.srcBinaryMode = ('b' if tparams.get('srcBinaryMode', False) else '')
      self.destBinaryMode = ('b' if tparams.get('destBinaryMode', False) else '')
    chunkSize = tparams.get('chunkSize', 32768)

    self.force = tparams.get(Dict.paramForce, False)

    fileNameTransforms = OS.Path.AsList(tparams.get('fileNameTransforms', None))
    fileFilters = OS.Path.AsList(tparams.get('fileFilters', None))
    dataFilters = OS.Path.AsList(tparams.get('dataFilters', None))

    self.failOnError = tparams.get(Dict.paramFailOnError, True)
    self.verbose = tparams.get('verbose', False)
    self.quiet = tparams.get(Dict.paramQuiet, False)
    if self.quiet:
      self.failOnError = False
    self.errors = 0

    # Setup destination.
    self.destFile = None
    self.closeDestFile = False
    dest = tparams.get(Dict.paramDestDirName, None)
    if not dest:
      dest = tparams.get(Dict.paramDestFile, None)
      if dest:
        self.destFile = True
    if dest:
      if 'write' in dir(dest):
        self.destFile = dest
      else:
        dest = os.path.normpath(dest)
        if not os.path.exists(dest):
          if tparams.get('failIfDestNotExists', False):
            raise AttaError(self, Dict.errFileOrDirNotExists % dest)
          try:
            if self.destFile:
              OS.MakeDirs(os.path.dirname(dest))
              self.destFile = open(dest, 'w' + self.destBinaryMode)
              self.closeDestFile = True
            else:
              OS.MakeDirs(dest)
          except Exception as E:
            self.HandleError(E, dest)
            return None
        else:
          if tparams.get('failIfDestExists', False):
            raise AttaError(self, Dict.errFileOrDirExists % dest)
          if os.path.isdir(dest):
            if self.destFile:
              raise AttaError(self, '%s is a directory instead of the file.' % dest)
          else:
            try:
              if self.force:
                OS.SetReadOnly(dest, False)
              self.destFile = open(dest, 'r+' + self.destBinaryMode)
              self.closeDestFile = True
            except Exception as E:
              self.HandleError(E, dest)
              return None

    # Handle 'append' parameter.
    try:
      if self.destFile:
        if tparams.get('append', True): self.destFile.seek(0, os.SEEK_END)
        else: self.destFile.truncate(0)
    except Exception as E:
      self.HandleError(E, dest)
      return None

    # Filter files.
    try:
      fntParams = tparams.copy()
      if Dict.paramDestDirName in fntParams:
        del fntParams[Dict.paramDestDirName]

      self.srcs = ExtendedFileSet(srcs)
      self.processedFiles = 0
      self.skippedFiles = 0
      if not self.quiet:
        self.LogStart()

      for rn, fn in self.srcs:
        sfn = os.path.normpath(os.path.join(rn, fn))
        dfn = None if dest else sfn
        process = True
        try:
          if not self.destFile:
            # When the destination is not a single file (== is directory),
            # then invoke registered file names transformations.
            if dest:
              dfn = os.path.normpath(os.path.join(dest, fn))
            for fntrans in fileNameTransforms:
              ndfn = fntrans(rn, fn, dest, dfn, caller = self, **fntParams)
              if ndfn:
                dfn = ndfn

          # Invoke registered files filters.
          for ffilter in fileFilters:
            if not ffilter(sfn, dfn, caller = self, **tparams):
              process = False
              break

          if not process:
            self.skippedFiles += 1
            if not self.quiet:
              self.LogSkipped(sfn, dfn)

          else:
            self.StartProcessing(sfn, dfn)
            if not self.quiet:
              self.LogStartProcessing(sfn, (dfn if dfn else dest))

            # Call the Start method of the registered data filters.
            for dfilter in dataFilters:
              startFn = getattr(dfilter, 'Start', None)
              if startFn:
                startFn(sfn, dfn, caller = self, **tparams)

            # Prepare source file.
            sf = open(sfn, 'r' + self.srcBinaryMode)
            dfIsTempFile = False
            df = None
            try:
              # Prepare destination file.
              if self.destFile:
                df = self.destFile
              else:
                try:
                  # Check if the source and destination files are not the same file (in-place filter).
                  if dfn == sfn:
                    # If so then use a temporary file.
                    df = tempfile.SpooledTemporaryFile(mode = 'w' + self.destBinaryMode, max_size = 1024 * 1024)
                    dfIsTempFile = True
                  else:
                    # If not then create new physical file.
                    if os.path.exists(dfn):
                      if tparams.get('failIfExists', False):
                        raise AttaError(self, Dict.errFileExists % dfn)
                      if self.force:
                        OS.SetReadOnly(dfn, False)
                    else:
                      OS.MakeDirs(os.path.dirname(dfn))
                    df = open(dfn, 'w' + self.destBinaryMode)

                except AttaError:
                  raise
                except Exception as E3:
                  self.HandleError(E3, dfn)
                  try: sf.close()
                  except Exception as E4: self.HandleError(E4, sfn)
                  continue

              while True:
                # Read a piece of data from source file, apply data filters
                # and write processed data to destination file.
                if self.srcBinaryMode: data = sf.read(chunkSize)
                else: data = sf.readline()
                if not data:
                  break
                for dfilter in dataFilters:
                  call = getattr(dfilter, '__call__', None)
                  if call:
                    data = call(data, caller = self, **tparams)
                df.write(data)

            finally:
              # Always try to close files even if exception occured.
              if not dfIsTempFile:
                if df and df != self.destFile:
                  df.close()
              sf.close()

            if dfIsTempFile:
              # The temporary destination file becomes the source file (in-place filter).
              df.seek(0)
              if not self.force and OS.IsReadOnly(sfn):
                raise IOError(os.errno.EACCES, os.strerror(os.errno.EACCES), sfn)
              baksfn = sfn + '~'
              os.rename(sfn, baksfn)
              sf = open(sfn, 'w')
              try:
                while True:
                  data = df.read(chunkSize)
                  if not data:
                    break
                  sf.write(data)
              finally:
                sf.close()
                df.close()
              OS.RemoveFile(baksfn, force = True)

            # Call the End method of the registered data filters.
            for dfilter in dataFilters:
              endFn = getattr(dfilter, 'End', None)
              if endFn:
                endFn(caller = self, **tparams)

            self.EndProcessing(sfn, dfn)
            self.processedFiles += 1
            if not self.quiet:
              self.LogEndProcessing(sfn, dfn)

        except AttaError:
          raise
        except Exception as E2:
          self.HandleError(E2, sfn)

      if not self.quiet:
        self.LogEnd()

    finally:
      if self.closeDestFile and self.destFile:
        try:
          self.destFile.close()
        except Exception as E:
          self.HandleError(E, dest)

      self.destFile = None
      self.closeDestFile = False

  def StartProcessing(self, sfn, dfn):
    """TODO: description
    dfn can be None - it means out is a file-like object"""
    pass

  def EndProcessing(self, sfn, dfn):
    """TODO: description"""
    pass

  def HandleError(self, E, fileName):
    if self.failOnError:
      raise
    self.errors += 1
    if not self.quiet or self.LogLevel() == LogLevel.DEBUG:
      err = None
      if type(E) == IOError: err = E.errno
      elif type(E) == os.error: err = os.errno
      if err:
        self.Log(Dict.errOSErrorForX % (err, os.strerror(err), str(fileName)), level = LogLevel.ERROR)
      else:
        self.Log(Dict.errException % str(E), level = LogLevel.ERROR)

  def Log(self, msg = '', **args):
    if not Dict.paramLevel in args:
      args[Dict.paramLevel] = (LogLevel.VERBOSE if not self.verbose else LogLevel.WARNING)
    Task._Log(self, msg, **args)

  def LogStart(self):
    """TODO: description"""
    pass

  def LogSkipped(self, sfn, dfn):
    """TODO: description"""
    self.Log(Dict.msgSkipped % sfn)

  def LogStartProcessing(self, sfn, dfn):
    """TODO: description"""
    if sfn == dfn:
      self.Log(sfn)
    else:
      self.Log(Dict.msgXtoY % (sfn, dfn))

  def LogEndProcessing(self, sfn, dfn):
    """TODO: description"""
    pass

  def LogEnd(self):
    """TODO: description"""
    if self.processedFiles or self.skippedFiles:
      self.Log(Dict.msgProcessedAndSkipped % (self.processedFiles, self.skippedFiles),
                 level = (LogLevel.INFO if not self.verbose else LogLevel.WARNING))
