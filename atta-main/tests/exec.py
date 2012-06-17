## \brief Exec task tests.

from pyant import *

Project.defaultTarget = 'test'

class test(Target):
  def Run(self):
    Echo('Exec test')
    Exec('exec.bat', ['1','2','3'], useShell = False)
    Exec('cmd', ['/c', 'dir', '*.py'])
    Exec('git', ['status'])
    Exec('echo', ['1','2','3'])
    Echo(Env.cwd)
    pass
