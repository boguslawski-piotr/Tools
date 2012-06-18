## \brief PyExec task tests.

from atta import *

Project.defaultTarget = 'test'

class test(Target):
  def Run(self):
    Echo('PyExec test')
    PyExec('pyexec_1', ['1','2','3'], useShell = False)