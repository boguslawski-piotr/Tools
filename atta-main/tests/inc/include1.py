'''Includes test.'''

from atta import *

Echo('In: ' + file.name)

class test1(Target):
  def Run(self):
    Echo('inc.include1.test1 target')

Echo('In: ' + file.name)