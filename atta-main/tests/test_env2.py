## \brief Exec task and environments variables tests.

from atta import *

project.defaultTarget = 'test'

class test(Target):
  def Run(self):
    project.env['test_env2'] = project.fileName
    # TODO: linux, mac os x
    Exec('test_env2.bat', ['1','2','3'], useShell = False)
    Echo(project.env['test_env2'])
