'''.. Data manipulation: TODO'''
import os
import types

from ..tools.Misc import LogLevel
from ..tools.Sets import ExtendedFileSet
from ..tools import OS
from .. import Dict
from .. import AttaError
from .Base import Task

class Filter(Task):
  '''
  TODO: description

  Parameters:
  
  * **srcs** -                     TODO Exactly the same as `srcs` in :py:class:`.ExtendedFileSet`
  
  * **dest** - can be: directory, file name (if not exists then always directory) or file like object
  * **failIfDestNotExists** - |False| for dir or file name 
  * **append** - |True| for file name or file like object
  
  * **binaryMode** - |False|
  * **chunkSize** - 32768
  
  * **fileNameTransforms**
    Valid if dest is a directory. 
  
  * **fileFilters** - one or more (list) functions implements IFileFilterFn, first False stops further checking (if list)
    Ten filtr moze sluzyc do eliminowania przetwarzania dla niektorych plikow.
    Np. w Copy z ustawionym: kopiuj tylko gdy nowsze.
    Itp. itd.
    
  * **dataFilters** - one or more (list) functions implements IDataFilterFn or instance of class implements IDataFilter (minimum __call__)
  
  
  Interfaces:
  
  .. code-block:: python
    
    def IFileNameTransformFn(srcRootDirName, srcFileName, destDirName, actualDestFileName)
      # must return destFileName or None if you want to use the default name:
      #   os.path.join(destDirName, srcRootDirName, srcFileName)
      # examples: 
      #   flatten: return os.path.join( destDirName, os.path.basename(srcFileName) )
      #   regexp: return re.sub('(.*\.)(java)$', (lambda m: m.group(1) + 'py'), actualDestFileName)     
     
    def IFileFilterFn(srcFileName, destFileName):
      # must return True if src is meant to be further processed
      # if returns False then file is skipped
      # destFileName may be None
       
    def IDataFilterFn(data):
      # data operations
      return data
    
    class IDataFilter:
      def Start(self, srcFileName, destFileName):
        # return ignored (yet)
        # src is not open
        # dest may not exists
        
      def __call__(self, data):
        # data operations
        return data
      
      def End(self):
        # return ignored (yet)
        # src is closed
        # dest should exists and is closed
  '''
  def __init__(self, srcs, dest, **tparams):
    self._DumpParams(locals())
    
    # Parameters.
    binaryMode = tparams.get('binaryMode', False)
    binaryMode = ('b' if binaryMode else '')
    chunkSize = tparams.get('chunkSize', 32768)
    
    fileNameTransforms = OS.Path.AsList(tparams.get('fileNameTransforms'), None)
    fileFilters = OS.Path.AsList(tparams.get('fileFilters'), None)
    dataFilters = OS.Path.AsList(tparams.get('dataFilters'), None)
    
    # Setup destination.
    outFile = None
    closeOutFile = False
    if 'write' in dir(dest):
      outFile = dest
    else:
      if tparams.get('failIfDestNotExists', False) and not os.path.exists(dest):
        raise AttaError(self, Dict.errFileOrDirNotExists % dest) 
      if not os.path.exists(dest):
        OS.MakeDirs(dest)
      else:
        if not os.path.isdir(dest):
          outFile = open(dest, 'r+' + binaryMode)
          closeOutFile = True
          
    # Filter files.
    try:
      if tparams.get('append', True) and outFile:
        outFile.seek(0, os.SEEK_END)
        
      filesSet = OS.Path.AsList(srcs)
      for rn, fn in ExtendedFileSet(filesSet):
        sfn = os.path.normpath(os.path.join(rn, fn))
        dfn = None
        process = True
        
        if not outFile:
          dfn = os.path.normpath(os.path.join(dest, rn, fn))
          for fntrans in fileNameTransforms:
            ndfn = fntrans(rn, fn, dest, dfn)
            if ndfn:
              dfn = ndfn
        
        # fileFilters
        for ffilter in fileFilters:
          if not ffilter(sfn, dfn):
            process = False
            break
        
        if process:
          if dfn == sfn:
            raise AttaError(self, 'Destination: %s points to source: %s' % (dfn, sfn))
        
          for dfilter in dataFilters:
            startFn = getattr(dfilter, 'Start', None)
            if startFn:
              startFn(sfn, dfn)
          
          sf = open(sfn, 'r' + binaryMode)
          of = None
          try:
            if dfn:
              OS.MakeDirs(os.path.dirname(dfn))
              of = open(dfn, 'w' + binaryMode)
              # TODO: force option
              # TODO: failIfExists option?
            else:
              of = outFile
            while True:
              if binaryMode:
                data = sf.read(chunkSize)
              else:
                data = sf.readline()
              if not data:
                break
              
              # Apply data filters.
              for dfilter in dataFilters:
                data = dfilter(data)
              
              # Write data to output file.  
              of.write(data)
              
          finally:
            # Close files and invoke...? TODO
            if of and not outFile:
              of.close()
            sf.close()
            for dfilter in dataFilters:
              endFn = getattr(dfilter, 'End', None)
              if endFn:
                endFn()
    
    finally:
      if closeOutFile and outFile:
        outFile.close()
      