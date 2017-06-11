"""Exec task and environments variables tests."""

from atta import *

Project.defaultTarget = 'test'

class test(Target):
  def Run(self):
    Project.env['test_env2'] = 'data from Atta'
    Echo('Atta: test_env2 is {0}'.format(Project.env['test_env2']))
    Exec('./test_env2${bat}', ['1', '2', '3'], useShell = False)
    Echo('Atta: test_env2 is {0}'.format(Project.env['test_env2']))
