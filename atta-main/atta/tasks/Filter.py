'''.. Data manipulation: TODO: filter'''
import os

from ..tools.Misc import LogLevel
from ..tools.Sets import ExtendedFileSet
from ..tools import OS
from .. import Dict
from .. import AttaError
from .Base import Task

class Filter(Task):
  '''
  TODO: description

  Required parameters:
  
  * **srcs** -                     TODO Exactly the same as `srcs` in :py:class:`.ExtendedFileSet`
    TODO: allow file like object(s)
  
  * **dest** - can be: directory, file name or file like object
  
  Parameters related to `dest` only:
  
  * **destIsAFile** - Indicates whether the `dest` is to be a directory or file. Valid when the `dest` does not exist. |False|
  * **append** - |True| for existing file or file like object. If False the file is truncated.
  * **failIfDestNotExists** |False| - for dir or file name
  * **failIfDestExists** |False| - For `dest` if it's a file name or directory.
    
  Parameters related to source files and created destination files:
  
  * **failIfExists** |False| - For created files if `dest` is a directory.
    TODO: change name (?)
    
  * **force** |False| -            When set to `True` then the files with read-only attribute are overriden.
    For `dest` if it's a file name or for created files if `dest` is a directory. 
    
  * **fileNameTransforms** - one or more (list) callables implements IFileNameTransform
    Valid only if `dest` is a directory. 
    
    .. code-block:: python
      
      def IFileNameTransform(srcRootDirName, srcFileName, 
                               destDirName, actualDestFileName, **tparams)
      
    Must return valid file name or `None` if you want to use the `actualDestFileName`.
    
  * **fileFilters** - one or more (list) callables implements IFileFilter, first False stops further checking (if list)
    Ten filtr moze sluzyc do eliminowania przetwarzania dla niektorych plikow.
    Np. w Copy z ustawionym: kopiuj tylko gdy nowsze.
    Itp. itd.
  
    .. code-block:: python

      def IFileFilter(srcFileName, destFileName, **tparams):
      
    Must return True if src is meant to be further processed.
    If returns False then file is skipped.
    `destFileName` may be `None`.
       
  * **dataFilters** - one or more (list) callable implements IDataFilter or instance of class that implements IDataFilter
  
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
    
  * **srcBinaryMode** - |False|
  * **destBinaryMode** - |False|
  * **binaryMode** - |False| 
  * **chunkSize** - 32768 for src, if srcBinaryMode/binaryMode is True

  * **failOnError**  |True| -      Controls whether an error stops the build or is only reported to the log.
  * **verbose** |False| -          Whether to show the name of each processed file. Even with log level set to WARNING.
  * **quiet** |False| -            Be extra quiet. No error is reported even with log level set to VERBOSE.
  
  '''
  def __init__(self, srcs, dest, **tparams):
    self.verbose = False
    self._DumpParams(locals())
    
    # Parameters.
    if 'binaryMode' in tparams:
      binaryMode = ('b' if tparams.get('binaryMode', False) else '')
      self.srcBinaryMode = binaryMode
      self.destBinaryMode = binaryMode
    else:
      self.srcBinaryMode = ('b' if tparams.get('self.srcBinaryMode', False) else '')
      self.destBinaryMode = ('b' if tparams.get('self.destBinaryMode', False) else '')
    chunkSize = tparams.get('chunkSize', 32768)
    
    self.force = tparams.get('force', False)
    
    fileNameTransforms = OS.Path.AsList(tparams.get('fileNameTransforms', None))
    fileFilters = OS.Path.AsList(tparams.get('fileFilters', None))
    dataFilters = OS.Path.AsList(tparams.get('dataFilters', None))
    
    self.failOnError = tparams.get('failOnError', True)
    self.verbose = tparams.get('verbose', False)
    self.quiet = tparams.get('quiet', False)
  
    # Setup destination.
    destFile = None
    closeDestFile = False
    if 'write' in dir(dest):
      destFile = dest
    else:
      if not os.path.exists(dest):
        if tparams.get('failIfDestNotExists', False):
          raise AttaError(self, Dict.errFileOrDirNotExists % dest) 
        try:
          if tparams.get('destIsAFile', False):
            destFile = open(dest, 'w' + self.destBinaryMode)
            closeDestFile = True
          else:  
            OS.MakeDirs(dest)
        except Exception as E:
          self.HandleError(E, dest)
          return None
      else:
        if tparams.get('failIfDestExists', False):
          raise AttaError(self, Dict.errFileOrDirExists % dest) 
        if not os.path.isdir(dest):
          try:
            if self.force:
              OS.SetReadOnly(dest, False)
            destFile = open(dest, 'r+' + self.destBinaryMode)
            closeDestFile = True
          except Exception as E:
            self.HandleError(E, dest)
            return None
          
    # Handle 'append' parameter.
    try:
      if destFile:
        if tparams.get('append', True): destFile.seek(0, os.SEEK_END)
        else: destFile.truncate(0)
      else:
        dest = os.path.normpath(dest)
    except Exception as E:
      self.HandleError(E, dest)
      return None
        
    # Filter files.
    try:
      self.srcs = ExtendedFileSet(srcs)
      self.processedFiles = 0
      self.skippedFiles = 0
      if not self.quiet: 
        self.LogStart()
      for rn, fn in self.srcs:
        sfn = os.path.normpath(os.path.join(rn, fn))
        dfn = None
        process = True
        try:
          if not destFile:
            # When the target is not a single file, then invoke registered file names transformations.
            dfn = os.path.normpath(os.path.join(dest, fn))
            for fntrans in fileNameTransforms:
              ndfn = fntrans(rn, fn, dest, dfn, **tparams)
              if ndfn:
                dfn = ndfn
          
          # Invoke registered files filters.
          for ffilter in fileFilters:
            if not ffilter(sfn, dfn, **tparams):
              process = False
              break
          
          if not process:
            self.skippedFiles += 1
            if not self.quiet: self.LogSkipped(sfn, dfn)
          else:
            self.StartProcessing(sfn, dfn)
            if not self.quiet: 
              self.LogStartProcessing(sfn, dfn)
            
            if dfn == sfn:
              # TODO: handle this, if option set then create temp file and if everything OK then override src + warning
              raise AttaError(self, 'Destination: %s points to source: %s' % (dfn, sfn))
          
            # Call the Start method of the registered data filters.
            for dfilter in dataFilters:
              startFn = getattr(dfilter, 'Start', None)
              if startFn:
                startFn(sfn, dfn, **tparams)
            
            # Prepare source file.
            sf = open(sfn, 'r' + self.srcBinaryMode)
            df = None
            try:
              # Prepare destination file.
              if not dfn:
                df = destFile
              else:
                try:
                  if os.path.exists(dfn):
                    if tparams.get('failIfExists', False):
                      raise AttaError(self, Dict.errFileExists % dfn) 
                    if self.force:
                      OS.SetReadOnly(dfn, False)
                  else:
                    OS.MakeDirs(os.path.dirname(dfn))
                  df = open(dfn, 'w' + self.destBinaryMode)
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
                    data = call(data, **tparams)
                df.write(data)
                
            finally:
              # Close files.
              try:
                if df and not destFile:
                  df.close()
                sf.close()
              except Exception as E5: 
                self.HandleError(E5, sfn)
            
            # Call the End method of the registered data filters. 
            for dfilter in dataFilters:
              endFn = getattr(dfilter, 'End', None)
              if endFn:
                endFn(**tparams)
            
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
      if closeDestFile and destFile:
        try:
          destFile.close()
        except Exception as E:
          self.HandleError(E, dest)

  def StartProcessing(self, sfn, dfn):
    '''TODO: description'''
    pass
  
  def EndProcessing(self, sfn, dfn):
    '''TODO: description'''
    pass

  def HandleError(self, E, fileName):
    if self.failOnError:
      raise
    if not self.quiet or self.LogLevel() == LogLevel.DEBUG:
      err = None
      if type(E) == IOError: err = E.errno
      elif type(E) == os.error: err = os.errno
      if err:
        self.Log(Dict.errOSErrorForX % (err, os.strerror(err), str(fileName)), level = LogLevel.WARNING)
      else:
        self.Log(Dict.errException % str(E), level = LogLevel.WARNING)
    
  def Log(self, msg = '', **args):
    if not Dict.paramLevel in args:
      args[Dict.paramLevel] = (LogLevel.VERBOSE if not self.verbose else LogLevel.WARNING)
    Task._Log(self, msg, **args)

  def LogStart(self):
    '''TODO: description'''
    pass

  def LogSkipped(self, sfn, dfn):
    '''TODO: description'''
    self.Log(Dict.msgSkipped % sfn)
  
  def LogStartProcessing(self, sfn, dfn):
    '''TODO: description'''
    self.Log(Dict.msgProcessingXToY % (sfn, dfn))
  
  def LogEndProcessing(self, sfn, dfn):
    '''TODO: description'''
    pass
  
  def LogEnd(self):
    '''TODO: description'''
    self.Log(Dict.msgProcessedAndSkipped % (self.processedFiles, self.skippedFiles), level = (LogLevel.INFO if not self.verbose else LogLevel.WARNING))
