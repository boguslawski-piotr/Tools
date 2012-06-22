'''Exec task and environments variables tests.'''

from atta import *

project.defaultTarget = 'test'

class test(Target):
  def Run(self):
    project.env['test_env2'] = 'data from Atta'
    Echo('Atta: test_env2 is {0}'.format(project.env['test_env2']))
    # TODO: linux, mac os x
    Exec('test_env2.bat', ['1','2','3'], useShell = False)
    Echo('Atta: test_env2 is {0}'.format(project.env['test_env2']))
