""".. Miscellaneous: Various functions and classes"""

from .internal.Misc import ObjectFromClass
from .. import Dict

#------------------------------------------------------------------------------

def isiterable(obj):
  """TODO: description"""
  return not isinstance(obj, basestring) and getattr(obj, '__iter__', False)

def RemoveDuplicates(iterable, preserveOrder = True):
  """TODO: description
  elements must be hashable
  """
  if preserveOrder:
    seen = {}
    result = []
    for item in iterable:
      if item in seen: continue
      seen[item] = 1
      result.append(item)
  else:
    result = list(set(iterable))
  return result

#------------------------------------------------------------------------------

def strip(str):
  """TODO: description"""
  if str != None: return str.strip()
  return None

def lstrip(str):
  """TODO: description"""
  if str != None: return str.lstrip()
  return None

def rstrip(str):
  """TODO: description"""
  if str != None: return str.rstrip()
  return None

#------------------------------------------------------------------------------

class NamedFileLike:
  """TODO: description"""
  def __init__(self, fileName, f):
    self.fileName = fileName
    self.f = f

  def __del__(self):
    if self.f != None:
      self.f.close()
    self.f = None

  def __getattr__(self, name):
    attr = getattr(self.f, name, None)
    if not attr:
      raise AttributeError("%s instance has no attribute '%s'" % (self.__class__.__name__, name))
    return attr

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.__del__()
    return False

#------------------------------------------------------------------------------

class VarsExpander:
  """
  TODO: description
  """
  def __init__(self, _class):
    self._expander = ObjectFromClass(_class)

  def SetImpl(self, _class):
    """Sets variables expander class and returns previous class."""
    return self._expander.SetClass(_class)

  def Expand(self, txt, **tparams):
    """Expand variables in given text."""
    return self._expander.GetObject().Expand(txt, **tparams)

