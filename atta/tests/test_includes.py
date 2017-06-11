"""Includes test."""

from atta import *

Project.defaultTarget = 'test'

Echo('In: ' + File.name)

inc1n, inc1 = Project.Import('include1')

class test(Target):
  dependsOn = [inc1.test1]
  def Run(self):
    Project.Import('inc/include1')
    Project.RunTarget('inc.include1.test1')
    Echo('test_includes.test target')
    Echo('project property from_include1 = ' + Project.from_include1)

    Echo('run project "include2" within test_includes.test target')
    Project.RunProject(None, 'include2', ['go2'])

Echo('run project "include2" within test_includes')
Project.RunProject({}, 'include2', ['go2'])
Echo('project "include2" ended')
