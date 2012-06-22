'''Variables in texts tests.'''  

import os
import stat

import atta.tools.VariablesLikeAntExpander
from atta.tools.Misc import SetVariablesExpander
from atta import *

project.defaultTarget = 'test'

localData = 'local data...'

class VariablesLikeDOSExpander(atta.tools.VariablesLikeAntExpander.Expander):
  def VariablePattern(self):
    return '\%([\w\.]+)\%'
    
class test(Target):
  def Run(self):
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

    SetVariablesExpander(VariablesLikeDOSExpander)
    
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
