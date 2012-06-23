'''Exec and PyExec task big output tests.'''

from atta import *

Project.defaultTarget = 'test'

class test(Target):
  def Run(self):
    PyExec('exec_output', ['1000'], useShell = False)
    e = PyExec('exec_output', ['100'], logOutput = False, useShell = False)
    Echo(e.output)
