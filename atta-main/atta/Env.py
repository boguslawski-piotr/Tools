"""TODO: description"""
import sys
import os

from . import Atta, LogLevel, Dict, OS

class Env(dict):
  """
  Env class

  TODO: description
  """
  def __init__(self, environ):
    dict.__init__(self, environ)
    self['cwd'] = os.getcwd()

  def chdir(self, dirName):
    """TODO: description"""
    prevDirName = os.getcwd()
    os.chdir(dirName)
    self['cwd'] = os.getcwd()
    return prevDirName

  def which(self, fileNames):
    """TODO: description"""
    sysPATH = self.get(Dict.PATH)
    if sysPATH:
      for path in OS.Path.AsList(sysPATH, os.pathsep):
        path = path.replace('"', '').replace("'", '')
        for fn in OS.Path.AsList(fileNames):
          fn = os.path.join(path, fn)
          if os.path.exists(fn):
            return fn
    return None

  '''private section'''

  def _Dump(self):
    Atta.Log('*** Env', level = LogLevel.DEBUG)
    for key, value in self.iteritems():
      Atta.Log('Env.' + key + ' = ' + value, level = LogLevel.DEBUG)
    Atta.Log('***', level = LogLevel.DEBUG)
