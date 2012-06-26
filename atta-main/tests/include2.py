'''Includes test.'''

from atta import *

Echo('In: ' + File.name)

class init2(Target):
  def Run(self):
    Echo('include2.init2 target')
    
class go2(Target):
  dependsOn = [init2]
  def Run(self):
    Echo('include2.test2 target')
