'''Includes test.'''

from atta import *

Echo('In: ' + file.name)

class init1(Target):
  def Run(self):
    Echo('include1.init1 target')
    
class test1(Target):
  DependsOn = [init1]
  def Run(self):
    Echo('include1.test1 target')
    project.from_include1 = 'i1'
