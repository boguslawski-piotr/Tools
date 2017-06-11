"""TODO: description"""
import os

from .tools.Misc import isiterable
from .Env import Env
from . import Dict, LogLevel, Atta, _GetProject

class Activity:
  """
  Base class for all targets, tasks and other executive classes.

  TODO: description
  """
  def LogLevel(self):
    return Atta.LogLevel()

  def Log(self, msg = '', **args):
    self._Log(msg, **args)

  def LogIterable(self, msg, iterable, **args):
    self._LogIterable(msg, iterable, **args)

  @property
  def Project(self):
    return _GetProject()

  def Env(self):
    if not self.Project:
      env = Env(os.environ)
    else:
      env = self.Project.env
    return env

  '''private section'''

  def _Type(self):
    return ''

  def _Name(self):
    return ''

  def _Log(self, msg = '', **args):
    args[self._Type()] = self._Name()
    Atta.Log(msg, **args)

  def _LogIterable(self, msg, iterable, **args):
    args[self._Type()] = self._Name()
    Atta.LogIterable(msg, iterable, **args)

  def _DumpParams(self, locals_):
    if Atta.LogLevel() == LogLevel.DEBUG:
      self._Log(Dict.msgDumpParameters)
      for name, value in locals_.items():
        if name != 'self':
          if isiterable(value):
            self._LogIterable('{0}:'.format(name), value)
          else:
            self._Log('{0}: {1}'.format(name, value))
      self._Log('')
