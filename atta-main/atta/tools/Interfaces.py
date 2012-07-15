""".. no-user-reference:"""
import types
from .internal.Misc import ObjectFromClass

class Observable:
  """The Observable class is a simple mixin class which can be used
     to make container objects "observable". An observable container
     issues events when being modified, and external "observers"
     can subscribe to such events.
  """
  __observers = None

  def addObserver(self, observer):
    """Adds new observer. It can be class or function that implements IObserver."""
    if not self.__observers:
      self.__observers = []
    if types.FunctionType == type(observer):
      self.__observers.append((None, observer))
    else:
      observer = ObjectFromClass(observer)
      self.__observers.append((observer, observer.GetObject()))

  def removeObserver(self, observer):
    """Removes *observer*."""
    try:
      if types.FunctionType == type(observer):
        self.__observers.remove((None, observer))
      else:
        for i, (c, o) in enumerate(self.__observers) or ():
          if observer == c.GetClass():
            del self.__observers[i]
            break
    except:
      pass

  def notifyObservers(self, event, *params, **tparams):
    for c, o in self.__observers or ():
      o(self, event, *params, **tparams)

def IObserver(caller, event, *params, **tparams):
  """TODO: description"""
  pass

#------------------------------------------------------------------------------

class IVarsExpander:
  """
  IVarsExpander interface

  TODO: description
  """
  def Expand(self, txt, **tparams):
    pass

#------------------------------------------------------------------------------

class IArchiveFile:
  def __init__(self, fileName, mode, password = None, **tparams):
    pass
  def close(self):
    pass
  def CanWrite(self):
    pass
  def write(self, file_, arcName):
    pass
  def writestr(self, data, arcName):
    pass
  def CanRead(self):
    pass
  def read(self, fileName, password = None):
    pass
  def FileTime(self, fileName):
    pass
  def HasCRCs(self):
    pass
  def FileCRCn(self, fileName):
    pass
  def FileCRC(self, fileName):
    pass

#------------------------------------------------------------------------------

class IVersionStrategy:
  """TODO: description"""
  def NextMajor(self, v):
    """TODO: description"""
    pass
  def NextMinor(self, v):
    """TODO: description"""
    pass
  def NextPath(self, v):
    """TODO: description"""
    pass
  def NextBuild(self, v):
    """TODO: description"""
    pass
