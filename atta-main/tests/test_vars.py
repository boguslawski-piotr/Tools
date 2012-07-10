'''Variables in texts tests.'''
from atta import *

Project.defaultTarget = 'test'

localData = 'local data...'

import atta.tools.DefaultVarsExpander

class VarsLikeDOSExpander(atta.tools.DefaultVarsExpander.Expander):
  def VariablePattern(self):
    return '\%([\w\.]+)\%'

class test(Target):
  def Run(self):
    v1s = 'test'
    v1t = Atta.VarsExpander().Expand('${test_ref}', test_ref = v1s)
    assert v1s == v1t

    Echo('''
Use of Ant style variables    
  var1: ${var1}
  var2 (not defined): ${var2}
  var3 (reference to var1): ${var3}
  project.dirName: ${atta.Project.dirName}
  localData: ${test_vars.localData}
  notDefined: ${test_vars.notDefined}
''',
    var1 = 'var 1 contents',
    var3 = '${var1}')

    pc = Atta.VarsExpander().SetImpl(VarsLikeDOSExpander)

    v1s = 'test'
    v1t = Atta.VarsExpander().Expand('%test_ref%', test_ref = v1s)
    assert v1s == v1t

    Echo('''
And now DOS, Windows style variables    
  var1: %var1%
  var2 (not defined): %var2%
  var3 (reference to var1): %var3%
  project.dirName: %atta.Project.dirName%
  localData: %test_vars.localData%
  notDefined: %test_vars.notDefined%
''',
    var1 = 'var 1 contents',
    var3 = '%var1%')

    Atta.VarsExpander().SetImpl(pc)
