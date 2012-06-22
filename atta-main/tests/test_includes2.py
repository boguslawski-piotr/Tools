'''Includes 2 test.'''

import sys
import os
from atta import *

Echo('0 In: ' + file.name)
Echo('0 cwd: ' + os.getcwd())

project.Import('inc/includes2')

Echo('0 In: ' + file.name)

Echo()
Echo('includes3.includes3_x = ' + sys.modules['includes3'].includes3_x)

project.RunTarget('includes2.includes2')
project.RunTarget('inc2.includes2.includes2')
project.RunTarget('inc.inc2.includes2.includes2')

project.defaultTarget = 'test'

class test(Target):
  DependsOn = ['inc.inc2.includes2.includes2', 'xtests.includes2.includes2']
  def Run(self):
    Echo('includes2 target')
    
project.Import('../xtests/includes2')    

project.RunTarget('...xtests.includes2.includes2')

project.Import('test_includes2')
