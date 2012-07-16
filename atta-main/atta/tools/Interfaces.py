""".. no-user-reference:"""
import types
from .internal.Misc import ObjectFromClass

def AbstractMethod(method):
  """TODO: description"""
  method.__abstract = True
  return method

def IsAbstractMethod(method):
  """TODO: description"""
  return '__abstract' in dir(method)

class Observable:
  """The Observable class is a simple mixin class which can be used
     to make container objects "observable". An observable container
     issues events when being modified, and external "observers"
     can subscribe to such events.

     Example:

     .. code-block:: python

      class o0():
        def __call__(self, c, event):
          print 'o0', event

      class o1(object):
        def __call__(self, c, event):
          print 'o1', event

      def o2(c, event):
        print 'o2', event

      class X(Observable):
        def action(self):
          self.NotifyObservers(1)

      x = X()
      io0 = x.AddObserver(o0)
      io1 = x.AddObserver(o1)
      io2 = x.AddObserver(o2)
      x.action()
      x.RemoveObserver(io2)
      x.action()
      x.RemoveObserver(io0)
      x.action()
  """
  def AddObserver(self, observer):
    """Adds new *observer*. It can be class or function that implements IObserver.
       Returns object that can be used as parameter in :py:meth:`.RemoveObserver`."""
    if not self.__observers:
      self.__observers = []
    if types.FunctionType == type(observer):
      self.__observers.append((None, observer))
    else:
      observer = ObjectFromClass(observer)
      self.__observers.append((observer, observer.GetObject()))
    return observer

  def RemoveObserver(self, observer):
    """Removes *observer*."""
    try:
      if types.FunctionType == type(observer):
        self.__observers.remove((None, observer))
      else:
        for i, (c, o) in enumerate(self.__observers) or ():
          if observer == c:
            del self.__observers[i]
            break
    except Exception:
      pass

  def NotifyObservers(self, event, *params, **tparams):
    """TODO: description"""
    for c, o in self.__observers or ():
      o(self, event, *params, **tparams)

  #: Only as safeguard.
  __observers = None

def IObserver(caller, event, *params, **tparams):
  """TODO: description"""
  assert False

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
