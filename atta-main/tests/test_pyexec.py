'''PyExec task tests.'''

from atta import *

project.defaultTarget = 'test'

class test(Target):
  def Run(self):
    Echo('PyExec test')
    PyExec('external', ['1','2','3'], useShell = False)
