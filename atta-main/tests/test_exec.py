'''Exec task tests.'''

from atta import *

Project.defaultTarget = 'test'

class test(Target):
  def Run(self):
    Echo('Exec test')
    
    # Macro: ${bat}, ${cmd} or ${exe}: On Windows will add .bat/.cmd/.exe to 
    # the executable name, on other systems will not add anything.
    # Macro ${sh}: on non Windows systems will add .sh, on Windows will add .bat.
    Exec('test_exec${bat}', ['1','2','3'], useShell = False)
    
    if OS.IsWindows():
      Exec('cmd', ['/c', 'dir', '*.py'])
    else:
      Exec('ls', ['*.py'])

    Exec('git', ['status'])
    
    Exec('echo', ['1','2','3'])
    e = Exec('echo', ['4','5','6'], logOutput = False, failOnError = False)
    if e.returnCode == 0:
      Echo(e.output)

    Exec('echo')
