'''PyExec task tests.'''

from atta import *

Project.defaultTarget = 'test'

class test(Target):
  def Run(self):
    Echo('PyExec test')
    PyExec('external', ['1','2','3'], useShell = False)
