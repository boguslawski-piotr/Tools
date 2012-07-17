""".. Miscellaneous: TODO"""
from .internal.Misc import ObjectFromClass

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

