## \brief Includes 2 test.

import os
from atta import *

Echo('  1 In: ' + file.name)
Echo('  1 cwd: ' + os.getcwd())

project.Import('inc2/includes2')

Echo('  1 In: ' + file.name)

class includes2(Target):
  def Run(self):
    Echo('inc.includes2 target')
    