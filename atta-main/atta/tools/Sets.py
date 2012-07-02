'''.. Files, directories: Sets TODO'''
import os
import re

from Misc import Logger, LogLevel
import OS

class FileSet(list):
  '''       
    Creates a set of files...
    
    TODO: description
    
    :param string rootDir:     TODO
    :param includes:           TODO
    :type includes:            string or path (separator :) or list of strings
    :param excludes:           TODO
    :type excludes:            string or path (separator :) or list of strings
    :param boolean useRegExp:  TODO
    :param callable filter:    TODO
    :param boolean realPaths:  TODO
    :param boolean withRootDir: TODO
    :param boolean createEmpty: TODO
    
    :return: iterable TODO
    
  '''
  def __init__(self, rootDir = '.', includes = '*', excludes = [], **tparams):
    if not tparams.get('createEmpty', False):
      self.AddFiles(rootDir, includes, excludes, **tparams)

  def AddFiles(self, rootDir, includes = '*', excludes = [], **tparams):
    self.rootDir, files = self.MakeSet(rootDir, includes, excludes, onlyDirs = False, **tparams)
    self.extend(files)
    # TODO: how to handle rootDir if FileSet includes files from different roots?
    
  def MakeSet(self, rootDir, includes, excludes = [], **tparams):
    '''Creates a set of files.
    '''
    includes = OS.Path.AsList(includes)
    excludes = OS.Path.AsList(excludes)
    useRegExp = tparams.get('useRegExp', False)
    realPaths = tparams.get('realPaths', True)
    withRootDir = tparams.get('withRootDir', False)
    onlyDirs = tparams.get('onlyDirs', False)
    _filter = tparams.get('filter', None)
          
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
          if _filter is not None:
            if not _filter(rootDir, nameToAdd):
              nameToAdd = None
        if nameToAdd is not None:
          if realPaths:
            cwd = os.getcwd()
            os.chdir(rootDir)
            nameToAdd = os.path.realpath(nameToAdd)
            os.chdir(cwd)
          else:
            if withRootDir:
              nameToAdd = os.path.join(rootDir, nameToAdd)
          filesSet.append(nameToAdd)
          
    return (rootDir, filesSet)

  @staticmethod
  def Match(pattern, name, useRegExp = False):
    # Bechavior compatible with Ant:
    # There is one "shorthand": if a pattern ends with / or \, then ** is appended.
    if not useRegExp and (pattern.endswith('\\') or pattern.endswith('/')):
      pattern = pattern + '**'
    
    name = name.replace('\\', '/')
    #Logger.Log('+++\nFileSet:Match:name: {0}'.format(name), level = LogLevel.DEBUG)
    #Logger.Log('FileSet:Match:pattern: {0}'.format(pattern), level = LogLevel.DEBUG)
    
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
    
    #Logger.Log('FileSet:Match:regexp: {0}'.format(pattern), level = LogLevel.DEBUG)

    rc = re.match(pattern, name) is not None
    
    #Logger.Log('FileSet:Match: {0}\n+++'.format(rc), level = LogLevel.DEBUG)
    
    return rc

class DirSet(FileSet):
  ''' 
    Creates a set of directories...
    
    TODO: description
    
  '''
  def __init__(self, rootDir = '.', includes = '**/**', excludes = [], **tparams):
    self.AddDirs(rootDir, includes, excludes, **tparams)

  def AddDirs(self, rootDir, includes = '*', excludes = [], **tparams):
    self.rootDir, files = self.MakeSet(rootDir, includes, excludes, onlyDirs = True, **tparams)
    self.extend(files)
  
class ExtendedFileSet(list):
  '''
    TODO: description
    
    Parameters:
  
    * **srcs**        TODO
      if string: file/dir/wildcard name or path (separator :) in which each item may be: file/dir/wildcard name
      if list: each item may be: file/dir/wildcard name or FileSet
  
    Zwraca liste 2 elementowych krotek: (rootDirName, fileName)
  ''' 
  def __init__(self, srcs):
    self.AddFiles(srcs)
    
  def AddFiles(self, srcs):
    srcs = OS.Path.AsList(srcs)
    for src in srcs:
      if len(src) <= 0:
        continue
      if isinstance(src, FileSet):
        for fname in src:
          self.append((src.rootDir, os.path.relpath(fname, src.rootDir)))
      else:
        if OS.Path.HasWildcards(src):
          rootDir, includes = OS.Path.Split(src)
          for fname in FileSet(rootDir, includes, realPaths = False, withRootDir = False):
            self.append((rootDir, fname)) 
        else:
          if os.path.isdir(src):
            for fname in FileSet(src, includes = '**/*', realPaths = False, withRootDir = False):
              self.append((src, fname)) 
          else:
            src = os.path.normpath(src)
            if os.path.exists(src):
              self.append(os.path.dirname(src), os.path.basename(src))
    