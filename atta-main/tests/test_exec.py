'''Exec task tests.'''

from atta import *

project.defaultTarget = 'test'

class test(Target):
  def Run(self):
    Echo('Exec test')
    # TODO: linux, mac os x
    Exec('test_exec.bat', ['1','2','3'], useShell = False)
    Exec('cmd', ['/c', 'dir', '*.py'])
    
    Exec('git', ['status'])
    
    Exec('echo', ['1','2','3'])
    e = Exec('echo', ['4','5','6'], logOutput = False, failOnError = False)
    if e.returnCode == 0:
      Echo(e.output)
