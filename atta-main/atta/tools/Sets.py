import os
import re

from ..BaseClasses import Task
from ..Log import Log, LogLevel

class FileSet(Task, list):
  '''       
  .. snippet:: FileSet
    
    .. code-block:: python
    
      FileSet(rootDir, include[, excludes, \*\*tparams])
    
    Creates a set of files...
    
    TODO:
    
  .. snippet:: FileSetParams
  
    :param string rootDir:     TODO
    :param includes:           TODO
    :type includes:            string or list of strings
    :param excludes:           TODO
    :type excludes:            string or list of strings
    :param boolean useRegExp:  TODO
    :param boolean realPaths:  TODO
    
    :return: iterable TODO
    
  '''
  def __init__(self, rootDir = '.', includes = '*', excludes = [], **tparams):
    self.AddFiles(rootDir, includes, excludes, **tparams)

  def AddFiles(self, rootDir, includes = '*', excludes = [], **tparams):
    files = self.MakeSet(rootDir, includes, excludes, onlyDirs = False, **tparams)
    self.extend(files)
    
  def MakeSet(self, rootDir, includes, excludes = [], **tparams):
    '''Creates a set of files.
      
      .. todo::
        
        - optimize simple calls like MakeSet(includes = \*.log) for one directory
    '''
    if isinstance(includes, basestring):
      includes = [includes]
    if isinstance(excludes, basestring):
      excludes = [excludes]
    useRegExp = tparams.get('useRegExp', False)
    realPaths = tparams.get('realPaths', True)
    onlyDirs = tparams.get('onlyDirs', False)
          
    rootDir = os.path.normpath(rootDir)
    rootDir += os.path.sep
    filesSet = []
    for root, dirs, files in os.walk(rootDir):
      root = root.replace(rootDir, '')
      if len(root) > 0 and not root.endswith(os.path.sep): 
        root += os.path.sep
      
      if onlyDirs:
        names = dirs
      else:
        names = files
      
      for name in names:
        nameToAdd = None
        name = root + name
        for pattern in includes:
          if FileSet.Match(pattern, name, useRegExp):
            nameToAdd = name
            break
        for pattern in excludes:
          if FileSet.Match(pattern, name, useRegExp):
            nameToAdd = None
            break
        if nameToAdd is not None:
          if realPaths:
            cwd = os.getcwd()
            try: os.chdir(rootDir)
            except: pass
            nameToAdd = os.path.realpath(nameToAdd)
            os.chdir(cwd)
          filesSet.append(nameToAdd)
          
    return filesSet

  @staticmethod
  def Match(pattern, name, useRegExp = False):
    # Bechavior compatible with Ant:
    # There is one "shorthand": if a pattern ends with / or \, then ** is appended.
    if not useRegExp and (pattern.endswith('\\') or pattern.endswith('/')):
      pattern = pattern + '**'
    
    name = name.replace('\\', '/')
    Log('+++\nFileSet:Match:name: {0}'.format(name), level = LogLevel.DEBUG)
    Log('FileSet:Match:pattern: {0}'.format(pattern), level = LogLevel.DEBUG)
    
    if useRegExp:
      return re.match(pattern, name) is not None
    
    pattern = pattern.replace('\\', '/')
      
    DOT      = '\\.'
    ONE_CHAR = '.{1,1}'
    pattern = pattern.replace('.', DOT)
    pattern = pattern.replace('?', ONE_CHAR)
    
    ANY_DIR_TMP    = ':/'
    ANY_DIR        = '(.*/|\.{0,0})'
    ANY_CHAR_TMP   = '."'
    ANY_CHAR       = '.*'
    FILE_NAME_CHAR = '[^<>:"/\\|?*]'
    ANY_FILE_NAME_CHAR = FILE_NAME_CHAR + '*'
    
    pattern = pattern.replace('**/**', '**//**')  # prepare for next two lines
    pattern = pattern.replace('**/', ANY_DIR_TMP)
    pattern = pattern.replace('/**', ANY_CHAR_TMP)
    pattern = pattern.replace('*',   ANY_FILE_NAME_CHAR)

    pattern = pattern.replace(ANY_CHAR_TMP, ANY_CHAR)
    pattern = pattern.replace(ANY_DIR_TMP, ANY_DIR)
    pattern = '^' + pattern + '$'
    
    Log('FileSet:Match:regexp: {0}'.format(pattern), level = LogLevel.DEBUG)

    rc = re.match(pattern, name) is not None
    
    Log('FileSet:Match: {0}\n+++'.format(rc), level = LogLevel.DEBUG)
    
    return rc

class DirSet(FileSet):
  ''' 
    .. snippet:: DirSet
      
      .. code-block:: python
      
        DirSet(rootDir, include[, excludes, \*\*tparams])
      
      Creates a set of directories...
      
      TODO:
      
    .. snippetref:: FileSetParams
    
  '''
  def __init__(self, rootDir = '.', includes = '**/**', excludes = [], **tparams):
    self.AddDirs(rootDir, includes, excludes, **tparams)

  def AddDirs(self, rootDir, includes = '*', excludes = [], **tparams):
    files = self.MakeSet(rootDir, includes, excludes, onlyDirs = True, **tparams)
    self.extend(files)
  