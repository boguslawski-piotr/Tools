import sys
from .. import OS

#------------------------------------------------------------------------------ 

class ObjectFromClass:
  '''
  General class that allows you to dynamically 
  select the implementation of any interface.
  '''
  def __init__(self, _class = None):
    self._class = None
    self._object = None
    if _class is not None:
      self.SetClass(_class)
  
  def SetClass(self, _class):
    '''TODO:description'''
    oldClass = self._class
    if isinstance(_class, basestring):
      self._class = sys.modules[OS.Path.RemoveExt(_class)].__dict__[OS.Path.Ext(_class, False)]
    else:
      self._class = _class
    self._object = None
    return oldClass
  
  def GetClass(self):
    return self._class
  
  def GetObject(self):
    '''TODO:description'''
    if self._object is None:
      self._object = self._class()
    return self._object

