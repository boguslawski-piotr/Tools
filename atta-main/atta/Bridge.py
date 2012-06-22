import sys
import tools.OS as OS

class Bridge:
  '''
  .. snippet:: Bridge
  
    General class that allows you to dynamically 
    select the implementation of any interface.
  '''
  def __init__(self, _class):
    self._class = None
    self._object = None
    self.SetClass(_class)
  
  def SetClass(self, _class):
    oldClass = self._class
    if isinstance(_class, basestring):
      self._class = sys.modules[OS.RemoveExt(_class)].__dict__[OS.Ext(_class, False)]
    else:
      self._class = _class
    self._object = None
    return oldClass
  
  def GetImpl(self):
    if self._object is None:
      self._object = self._class()
    return self._object
