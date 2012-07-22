""".. Files, directories: Sets TODO: sets"""
import os

from .. import Dict
from .Misc import isstring
from . import OS

class FileSet(list):
  """
  Creates a set of files...

  TODO: description

  * **rootDirName** `(.)`             - TODO
  * **includes** `(*)`            - TODO string or path (separator :) or list of strings
  * **excludes** |None|           - TODO string or path (separator :) or list of strings
  * **useDefaultExcludes** |True| - TODO
  * **useRegExp** |False|         - TODO
  * **filters** |None|            - TODO
  * **followLinks** |False|       - TODO
  * **failOnError** |False|       - Controls whether an error while scanning files and directories raise an exception.
  * **realPaths** |False|         - TODO
  * **withRootDirName** |False|   - TODO
  * **createEmpty** |False|       - TODO

  Returns: TODO

  """
  def __init__(self, rootDirName = '.', includes = '*', excludes = None, **tparams):
    self.rootDirName = None
    if not tparams.get('createEmpty', False):
      self.AddFiles(rootDirName, includes, excludes, **tparams)

  DEFAULT_EXCLUDES = [
    # Miscellaneous typical temporary files
    "**/*~",
    "**/#*#",
    "**/.#*",
    "**/%*%",
    "**/._*",

    # CVS
    "**/CVS",
    "**/CVS/**",
    "**/.cvsignore",

    # SCCS
    "**/SCCS",
    "**/SCCS/**",

    # Visual SourceSafe
    "**/vssver.scc",

    # Subversion
    "**/.svn",
    "**/.svn/**",

    # Mac
    "**/.DS_Store",

    # Git
    '**/.git',
    '**/.git/**',
    '**/.gitattributes',
    '**/.gitignore',
    '**/.gitmodules',

    # Mercurial
    '**/.hg',
    '**/.hg/**',
    '**/.hgignore',
    '**/.hgsub',
    '**/.hgsubstate',
    '**/.hgtags',

    # Baazar
    '**/.bzr',
    '**/.bzr/**',
    '**/.bzrignore',
  ]
  '''Definitions of files/directories that are excluded by default from any FileSet (and derived classes).'''

  def AddFiles(self, rootDirName, includes = '*', excludes = None, **tparams):
    self.rootDirName, files = self.MakeSet(rootDirName, includes, excludes, onlyDirs = False, **tparams)
    self.extend(files)
    # TODO: how to handle rootDirName if FileSet includes files from different roots (many AddFiles called)?

  def MakeSet(self, rootDirName, includes, excludes = None, **tparams):
    """Creates a set of files."""
    # Prepare parameters.
    includes = OS.Path.AsList(includes)
    excludes = OS.Path.AsList(excludes)
    useDefaultExcludes = tparams.get('useDefaultExcludes', True)
    useRegExp = tparams.get('useRegExp', False)
    realPaths = tparams.get('realPaths', False)
    withRootDirName = tparams.get('withRootDirName', False)
    filters = OS.Path.AsList(tparams.get('filters', None))
    followLinks = tparams.get('followLinks', False)
    failOnError = tparams.get(Dict.paramFailOnError, False)

    _onlyDirs = tparams.get('onlyDirs', False)
    _onlyFiles = tparams.get('onlyFiles', True)

    rootDirName = os.path.normpath(rootDirName)
    rootDirName += os.path.sep

    def OnError(E):
      if failOnError:
        raise E

    # Optimize simple calls.
    useWalk = False
    for pattern in includes:
      if isstring(pattern):
        if OS.Path.HasAntStyleWildcards(pattern) or pattern.find('/') >= 0 or pattern.find('\\') >= 0:
          useWalk = True
          break
    if not useWalk:
      # If there are no subdirectories and/or Ant-style wildcards
      # in includes then use the simplest directory list.
      tree = []
      try:
        tree = os.listdir(rootDirName)
      except os.error as E:
        OnError(E)
      dirs, nondirs = [], []
      for name in tree:
        if os.path.isdir(os.path.join(rootDirName, name)):
          dirs.append(name)
        else:
          nondirs.append(name)
      tree = [(rootDirName, dirs, nondirs)]
    else:
      # If includes are more bit complicated then
      # perform a full scan of the directory tree.
      tree = os.walk(rootDirName, onerror = OnError, followlinks = followLinks)

    # Collect files/directories.
    filesSet = []
    for root, dirs, files in tree:
      root = root.replace(rootDirName, '')
      if len(root) > 0 and not root.endswith(os.path.sep):
        root += os.path.sep

      if _onlyDirs:
        names = dirs
      elif _onlyFiles:
        names = files
      else:
        names = dirs + files

      for name in names:
        nameToAdd = None
        name = root + name
        for pattern in includes:
          if OS.Path.Match(pattern, name, useRegExp):
            nameToAdd = name
            break
        if nameToAdd:
          for pattern in excludes:
            if OS.Path.Match(pattern, nameToAdd, useRegExp):
              nameToAdd = None
              break
        if nameToAdd and useDefaultExcludes:
          for pattern in FileSet.DEFAULT_EXCLUDES:
            if OS.Path.Match(pattern, nameToAdd, False):
              nameToAdd = None
              break
        if nameToAdd:
          for flt in filters:
            if not flt(rootDirName, nameToAdd):
              nameToAdd = None
              break

        if nameToAdd:
          if realPaths:
            cwd = os.getcwd()
            os.chdir(rootDirName)
            nameToAdd = os.path.realpath(nameToAdd)
            os.chdir(cwd)
          else:
            if withRootDirName:
              nameToAdd = os.path.join(rootDirName, nameToAdd)
          filesSet.append(nameToAdd)

    return rootDirName, filesSet

class DirSet(FileSet):
  """
    Creates a set of directories...

    TODO: description

  """
  def __init__(self, rootDirName = '.', includes = '*', excludes = None, **tparams):
    self.AddDirs(rootDirName, includes, excludes, **tparams)

  def AddDirs(self, rootDirName, includes = '*', excludes = None, **tparams):
    self.rootDirName, files = self.MakeSet(rootDirName, includes, excludes, onlyDirs = True, **tparams)
    self.extend(files)

class DirFileSet(FileSet):
  """
    Creates a set of directories and files.

    TODO: description

  """
  def __init__(self, rootDirName = '.', includes = '*', excludes = None, **tparams):
    self.AddDirs(rootDirName, includes, excludes, **tparams)

  def AddDirs(self, rootDirName, includes = '*', excludes = None, **tparams):
    self.rootDirName, files = self.MakeSet(rootDirName, includes, excludes, onlyDirs = False, onlyFiles = False, **tparams)
    self.extend(files)

class ExtendedFileSet(list):
  """
    TODO: description

    Parameters:

    * **srcs**        TODO
      if string: file/dir/wildcard name or path (separator :) in which each item may be: file/dir/wildcard name
      if list: each item may be: file/dir/wildcard name or FileSet or DirSet
      also FileSet or DirSet alone

    Zwraca liste 2 elementowych krotek: (rootDirName, fileName)
  """
  def __init__(self, srcs, **tparams):
    self.AddFiles(srcs)

  def AddFiles(self, srcs, **tparams):
    # Prepare parameters.
    if isinstance(srcs, FileSet):
      srcs = [srcs]
    srcs = OS.Path.AsList(srcs)
    tparams['realPaths'] = False
    tparams['withRootDirName'] = False

    # Expand all into a flat list of files.
    for src in srcs:
      if isinstance(src, DirSet):
        for dname in src:
          src = FileSet(dname, '**/*', **tparams)
          for fname in src:
            self.append((src.rootDirName, fname))
      elif isinstance(src, FileSet):
        for fname in src:
          self.append((src.rootDirName, fname))
      else:
        if len(src) <= 0:
          continue
        if OS.Path.HasWildcards(src):
          if src.startswith('..'):
            l = src.rfind('../')
            rname, incls = src[:l + 3], src[l + 3:]
          elif src.startswith('/') or src.find(':') == 1:
            rname, incls = OS.Path.Split(src)
          else:
            rname, incls = '.', src
          for fname in FileSet(rname, includes = incls, **tparams):
            self.append((rname, fname))
        else:
          if os.path.isdir(src):
            for fname in FileSet(src, includes = '**/*', **tparams):
              self.append((src, fname))
          else:
            src = os.path.normpath(src)
            if os.path.exists(src):
              self.append((os.path.dirname(src), os.path.basename(src)))
