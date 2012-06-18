## \brief Exec task tests.

from atta import *

project.defaultTarget = 'test'

class test(Target):
  def Run(self):
    Echo('Exec test')
    Exec('test_exec.bat', ['1','2','3'], useShell = False)
    Exec('cmd', ['/c', 'dir', '*.py'])
    Exec('git', ['status'])
    Exec('echo', ['1','2','3'])
    e = Exec('echo', ['1','2','3'], logOutput = False, failOnError = False)
    if e.returnCode == 0:
      Echo(e.output)

