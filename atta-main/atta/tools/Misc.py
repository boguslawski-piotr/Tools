""".. Miscellaneous: Various functions and classes"""

def isstring(obj):
  """TODO: description"""
  return isinstance(obj, basestring)

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
  if str: return str.strip()
  return str

def lstrip(str):
  """TODO: description"""
  if str: return str.lstrip()
  return str

def rstrip(str):
  """TODO: description"""
  if str: return str.rstrip()
  return str

#------------------------------------------------------------------------------

class NamedFileLike:
  """TODO: description"""
  def __init__(self, fileName, f):
    self.fileName = fileName
    self.f = f

  def __del__(self):
    if self.f:
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
