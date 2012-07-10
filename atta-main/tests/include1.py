'''Includes test.'''

from atta import *

Echo('In: ' + File.name)

class init1(Target):
  def Run(self):
    Echo('include1.init1 target')

class test1(Target):
  dependsOn = [init1]
  def Run(self):
    Echo('include1.test1 target')
    Project.from_include1 = 'i1'
