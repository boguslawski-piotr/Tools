'''Includes 2 test.'''

import sys
import os
from atta import *

Echo('0 In: ' + File.name)
Echo('0 cwd: ' + os.getcwd())

Project.Import('inc/includes2')

Echo('0 In: ' + File.name)

Echo()
Echo('includes3.includes3_x = ' + sys.modules['includes3'].includes3_x)

Project.RunTarget('includes2.includes2')
Project.RunTarget('inc2.includes2.includes2')
Project.RunTarget('inc.inc2.includes2.includes2')

Project.defaultTarget = 'test'

class test(Target):
  dependsOn = ['inc.inc2.includes2.includes2', 'xtests.includes2.includes2']
  def Run(self):
    Echo('includes2 target')
    
Project.Import('../xtests/includes2')    

Project.RunTarget('...xtests.includes2.includes2')

Project.Import('test_includes2')
