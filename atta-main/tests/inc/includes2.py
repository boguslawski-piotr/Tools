"""Includes 2 test."""

import os
from atta import *

Echo('  1 In: ' + File.name)
Echo('  1 cwd: ' + os.getcwd())

Project.Import('inc2/includes2')

Echo('  1 In: ' + File.name)

class includes2(Target):
  def Run(self):
    Echo('inc.includes2 target')
