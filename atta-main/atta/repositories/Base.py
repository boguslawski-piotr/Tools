'''.. no-user-reference:'''
from ..tools.internal.Misc import ObjectFromClass
import atta.Dictionary as Dictionary
import Styles

class ARepository:
  '''TODO: description'''
  def __init__(self, data):
    self.data = data
    if data is not None:
      _styleClass = data.get(Dictionary.style, ARepository.GetDefaultStyleImpl())
    else:
      _styleClass = ARepository.GetDefaultStyleImpl()
    self._styleImpl = ObjectFromClass(_styleClass)
    
  _defaultStyleImpl = ObjectFromClass(Styles.Maven) 

  @staticmethod
  def SetDefaultStyleImpl(_class):
    ARepository._defaultStyleImpl = ObjectFromClass(_class)
  
  @staticmethod
  def GetDefaultStyleImpl():  
    return ARepository._defaultStyleImpl.GetClass()

  def Get(self, packageId, scope, store = None):
    '''TODO: description'''
    pass
  
  def Check(self, packageId, scope):
    '''TODO: description'''
    pass
  
  def Put(self, f, fBaseDirName, packageId):
    '''TODO: description'''
    pass
  
  def Clean(self, packageId): 
    '''TODO: description'''
    pass
    
  def _Name(self):
    '''TODO: description'''
    pass
  
