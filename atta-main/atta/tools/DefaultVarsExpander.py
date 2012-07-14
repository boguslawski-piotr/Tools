'''.. no-user-reference:'''
import sys
import re

class Expander:
  def Expand(self, txt, **tparams):
    '''
    Expand Ant like variables in given text.
    
    TODO: description
    If you use ``\${var}`` then result will be ``${var}``.
    Trying expanding 'var' will not be made. 
    
    Example:
    
    .. code-block:: python
    
      >>> funny = 'funny'
      >>> txt = 'The Atta is ${what} and ${__main__.funny}.'
      >>> txt = Expand(txt, what = 'cool')
      >>> print(txt)
      The Atta is cool and funny.
      
    .. todo::
    
      - add posibility to expand environment variables (przekazac env do tej funkcji)
      - write it from scratch and better
    '''
    # Expand variables except those that begin at the character '\'.
    escape = r'(^|[^\\])'
    vpattern = self.VariablePattern()
    while True:
      m = re.search(escape + vpattern, txt)
      if m is None:
        break
      paramName = m.group(2)
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
      txt = re.sub(vpatternl + paramName + vpatternr, str(param).replace('\\', '\\\\'), txt)

    # Normalize escaped variables.
    escape = r'([\\])'
    vpattern = escape + self.VariablePattern()
    while True:
      m = re.search(vpattern, txt)
      if m == None:
        break
      txt = txt.replace(m.group(0), m.group(0)[1:])

    return txt

  def VariablePattern(self):
    return '\$\{([\w\-\.]+)\}'
