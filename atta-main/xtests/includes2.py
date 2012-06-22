'''Includes 2 test.'''

import sys
import os
from atta import *

Echo('4 In: ' + file.name)
Echo('4 cwd: ' + os.getcwd())

class includes2(Target):
  def Run(self):
    Echo('xtests.includes2 target')