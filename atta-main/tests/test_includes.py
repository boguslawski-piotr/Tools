## \brief Includes test.

from atta import *
from atta.Project import Project

project.defaultTarget = 'test'

Echo('In: ' + file.name)

inc1n, inc1 = project.Import('include1')

class test(Target):
  DependsOn = [inc1.test1]
  def Run(self):
    project.Import('inc/include1')
    project.RunTarget('inc.include1.test1')
    Echo('test_includes.test target')
    Echo('project property from_include1 = ' + project.from_include1)
    
    Echo('run project "include2" within test_includes.test target')
    project.RunProject(None, 'include2', ['go2'])

Echo('run project "include2" within test_includes')
project.RunProject({}, 'include2', ['go2'])
Echo('project "include2" ended')
