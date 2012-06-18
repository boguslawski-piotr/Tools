## \brief Includes 2 test.

import sys
from atta import *

Echo('0 In: ' + file.name)

project.Import('inc/includes2')

Echo('1 In: ' + file.name)

Echo()
Echo('includes3.includes3_x = ' + sys.modules['includes3'].includes3_x)

project.RunTarget('inc.inc2.includes2.includes2')

project.defaultTarget = 'test'

class test(Target):
  DependsOn = ['inc.inc2.includes2.includes2']
  def Run(self):
    Echo('includes2 target')