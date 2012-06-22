'''Includes 2 test.'''

import sys
import os
from atta import *

Echo('    2 In: ' + file.name)
Echo('    2 cwd: ' + os.getcwd())

project.Import('../../includes3')

Echo('    2 In: ' + file.name)

class includes2(Target):
  def Run(self):
    Echo('inc.inc2.includes2 target')