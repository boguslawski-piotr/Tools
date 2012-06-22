'''
  .. snippet:: Misc
  
    TODO: description
'''
from ..Bridge import Bridge
import VariablesLikeAntExpander

_variablesExpander = Bridge(VariablesLikeAntExpander.Expander)

def SetVariablesExpander(_class):
  '''
  TODO: description
  '''
  return _variablesExpander.SetClass(_class)
      
def ExpandVariables(txt, **tparams):
  '''
  Expand "variables" in given text.
  More information about variables expanders 
  can be found in :py:class:`atta.Interfaces.IVariablesExpander`.
  '''
  return _variablesExpander.GetImpl().Expand(txt, **tparams)

