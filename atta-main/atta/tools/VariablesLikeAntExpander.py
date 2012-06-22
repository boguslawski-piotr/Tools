import sys
import re

class Expander:
  def Expand(self, txt, **tparams):
    '''
    Expand Ant like variables in given text.
    
    TODO: description
    
    Example:
    
    .. code-block:: python
    
      >>> funny = 'funny'
      >>> txt = 'The Atta is ${what} and ${__main__.funny}.'
      >>> txt = ExpandVariables(txt, what = 'cool')
      >>> print(txt)
      The Atta is cool and funny.
    '''
    vpattern = self.VariablePattern()
    while True:
      m = re.search(vpattern, txt)
      if m is None:
        break
      paramName = m.group(1)
      param = tparams.get(paramName, None)
      if param is None:
        param = paramName + '-NOT-FOUND'
        try:
          v = paramName.split('.')
          moduleName = ''
          for i in range(0, len(v) - 1):
            if len(moduleName) > 0: moduleName = moduleName + '.'
            moduleName = moduleName + v[i] 
            try: 
              _module = sys.modules[moduleName]
              _object = _module.__dict__[v[i + 1]]
              if i == len(v) - 2:
                param = _object
              else:
                param = getattr(_object, v[i + 2], param)
              param = '{0}'.format(param)
              break
            except:
              pass
        except:
          pass
      vpatternl = vpattern.split('(')[0]
      vpatternr = vpattern.split(')')[1]
      txt = re.sub(vpatternl + paramName + vpatternr, param.replace('\\', '\\\\'), txt)
    return txt

  def VariablePattern(self):
    return '\$\{([\w\.]+)\}'
  