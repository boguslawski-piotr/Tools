'''.. no-user-reference:'''
from ..tools.internal.Misc import ObjectFromClass
import Styles

class ARepository:
  '''TODO: description'''
  class Dictionary:
    '''TODO: description'''
    dependsOn  = 'dependsOn'
    repository = 'repository'
    style      = 'style'
    package    = 'package'
    groupId    = 'groupId'
    artifactId = 'artifactId'
    version    = 'version'
    type       = 'type'
    putIn      = 'putIn'
    ifNotExists= 'ifNotExists'
    
    rootDir    = 'rootDir'
    
    host       = 'host'
    port       = 'port'
    user       = 'user'
    pasword    = 'password'
    passive    = 'passive'
    useCache   = 'useCache'
    
  def __init__(self, data):
    self.data = data
    if data is not None:
      _styleClass = data.get(ARepository.Dictionary.style, ARepository.GetDefaultStyleImpl())
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

  def Get(self, packageId, store = None):
    '''TODO: description'''
    pass
  
  def Check(self, packageId):
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
  
