"""Includes 2 test."""

import sys
import os
from atta import *

Echo('    2 In: ' + File.name)
Echo('    2 cwd: ' + os.getcwd())

Project.Import('../../includes3')

Echo('    2 In: ' + File.name)

class includes2(Target):
  def Run(self):
    Echo('inc.inc2.includes2 target')
