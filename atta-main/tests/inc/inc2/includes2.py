## \brief Includes 2 test.

import sys
from atta import *

Echo('    0 In: ' + file.name)

project.Import('../../includes3')

Echo('    1 In: ' + file.name)

class includes2(Target):
  def Run(self):
    Echo('inc.inc2.includes2 target')